# Copilot Instructions: RECOIL_Datasets

These notes explain how this repo is organized and how to be productive quickly as an AI coding agent.

## What this repo is
- Purpose: distribute intermodal freight datasets (nodes, edges, demand) for the ARPA‑E RECOIL project.
- Two usage modes:
  - **Web app**: `voila.ipynb` served via Voilà in Docker for interactive on-demand exploration (5 examples).
  - **Jupyter notebook**: `usage.ipynb` with comprehensive examples and helper functions.
- Data is hosted remotely and fetched from: https://recoil.ise.utk.edu/data/Parsed_Data/ (BASE_URL).

## Key files and structure
- `README.md` — authoritative description of data contents, IDs, update history, and usage instructions.
- `voila.ipynb` — lightweight interactive web app with 5 on-demand examples (no heavy pre-execution).
- `usage.ipynb` — full Jupyter notebook with detailed data exploration workflows.
- `requirements.txt` — Python dependencies (pandas, requests, geopandas, shapely, matplotlib, voila, ipywidgets).
- `Dockerfile`, `docker-compose.yml`, `start.sh` — containerized Voilà app setup.
- `.github/copilot-instructions.md` — this file.
- `images/` — figures referenced by the README.

## Data model and conventions
- Three modes: H (Highway), R (Railway), W (Waterway).
- Node IDs are partitioned by mode (from README): R: 101–156, W: 201–248, H: 301–413. Nodes CSV referenced in the notebook: `intermodal-217.csv`.
- Edge pickles per mode: `H-adj.pickle`, `R-adj.pickle`, `W-adj.pickle`.
  - Each is a dict keyed by a pair of node IDs: (i, j). Two-way connections are assumed and keys are normalized so the smaller ID is first.
  - Each value has: i_lat, i_lon, j_lat, j_lon, mode, distance, path.
  - path is a tuple of (lat, lon) points; when building LineStrings, reverse to (lon, lat).
- Demand pickle: `demand.pickle` is a dict keyed by ordered OD pairs (i, j) (direction matters). Values include tons_2025, tons_2030, …, tons_2050.

## Notebook patterns to follow

### voila.ipynb (web app)
- Lightweight notebook served by Voilà with no heavy pre-execution.
- Five interactive examples using ipywidgets (on-demand button clicks):
  1. Basic node/edge exploration with city and mode filters
  2. Find intermodal neighbors for a given city
  3. Demand lookup between two cities (Highway nodes only)
  4. Dataset statistics (node/edge counts, total distances)
  5. Mode comparison (distance stats and bar chart)
- Helper functions defined inline: `load_pickle_from_url`, `create_geoframe_from_edges`, `find_connection_by_id`.
- Uses widgets.Output() to display results asynchronously when buttons are clicked.

### usage.ipynb (full notebook)
- Comprehensive examples for local Jupyter usage.
- BASE_URL is declared: `BASE_URL = 'https://recoil.ise.utk.edu/data/Parsed_Data/'`.
- Helper utilities defined:
  - `load_pickle_from_url(url)`: uses requests + pickle to load remote `.pickle` files with timeouts and basic error handling.
  - `create_geoframe_from_edges(edges, plot=False)`: converts the edges dict to a GeoDataFrame; reverses (lat, lon) → (lon, lat) for shapely LineString; optional plotting.
  - `filter_nodes_by_substring(df_nodes, column, substring)`: simple string contains filter.
  - `find_id_by_type(df, type_value)`, `find_connection_by_id(keys, id)`: helpers for selecting node IDs and neighbors.
- Typical flow:
  1) `df_nodes = pd.read_csv(f"{BASE_URL}intermodal-217.csv")`
  2) `demand = load_pickle_from_url(f"{BASE_URL}demand.pickle")`
  3) `water = load_pickle_from_url(f"{BASE_URL}W-adj.pickle")` (similarly for H and R)
  4) `gdf = create_geoframe_from_edges(water, plot=False)` then filter/visualize.

## Environment and dependencies
- The notebooks import: pandas, requests, geopandas, shapely, matplotlib. For the web app, also: voila, ipywidgets.
- Install from `requirements.txt`: `pip install -r requirements.txt`
- Docker setup: Build via `docker compose up --build` or `docker build -t recoil-voila:dev .`
- Container runs Voilà on port 8866, serving `voila.ipynb` by default (configurable via VOILA_NOTEBOOK env var).
- No build system or tests in this repo; treat it as a data distribution + notebook project.

## Docker and deployment
- `Dockerfile`: Python 3.11 slim base, installs deps from requirements.txt, runs as non-root user, uses tini for signal handling.
- `docker-compose.yml`: mounts repo as volume for live edits during development, exposes port 8866, sets container name `recoil-data-voila`.
- `start.sh`: bash wrapper that launches Voilà with `--strip_sources=False` to show code alongside outputs.
- Environment variables: VOILA_PORT (8866), VOILA_IP (0.0.0.0), VOILA_NOTEBOOK (voila.ipynb), BASE_URL (data source).

## Gotchas and tips
- Edge keys (i, j) are undirected and normalized min→max; demand keys (i, j) are directed — don't swap.
- Waterway nodes in README are also described in `intermodal-218.csv`; the notebook currently reads `intermodal-217.csv` for selected intermodal nodes. Prefer the notebook's BASE_URL + filenames for programmatic access.
- An update on 2025‑01‑03 changed `W-adj.pickle` mode string to 'W' — don't hardcode earlier assumptions.
- When building interactive widgets in voila.ipynb, use widgets.Output() contexts and on_click handlers to avoid execution on page load.

## Where to start
- **Web app**: Run `docker compose up --build`, open http://localhost:8866, click buttons to explore data on-demand.
- **Local notebook**: Open `usage.ipynb`, ensure the deps above are installed, run top→down. Use the helpers to load pickles and build GeoDataFrames.
- For quick examples in usage.ipynb, search for: `url_D`, `url_W`, `url_H`, `url_R`, and `create_geoframe_from_edges` to see concrete usage snippets.


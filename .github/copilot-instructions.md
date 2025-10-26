# Copilot Instructions: RECOIL_Datasets

These notes explain how this repo is organized and how to be productive quickly as an AI coding agent.

## What this repo is
- Purpose: distribute intermodal freight datasets (nodes, edges, demand) for the ARPA‑E RECOIL project; primary usage is via the example notebook `usage.ipynb`.
- Data is hosted remotely and fetched from: https://recoil.ise.utk.edu/data/Parsed_Data/ (BASE_URL in the notebook).

## Key files and structure
- `README.md` — authoritative description of data contents, IDs, and update history.
- `usage.ipynb` — runnable examples to explore nodes, demand, and adjacency pickles; defines helper functions.
- `images/` — figures referenced by the README.

## Data model and conventions
- Three modes: H (Highway), R (Railway), W (Waterway).
- Node IDs are partitioned by mode (from README): R: 101–156, W: 201–248, H: 301–413. Nodes CSV referenced in the notebook: `intermodal-217.csv`.
- Edge pickles per mode: `H-adj.pickle`, `R-adj.pickle`, `W-adj.pickle`.
  - Each is a dict keyed by a pair of node IDs: (i, j). Two-way connections are assumed and keys are normalized so the smaller ID is first.
  - Each value has: i_lat, i_lon, j_lat, j_lon, mode, distance, path.
  - path is a tuple of (lat, lon) points; when building LineStrings, reverse to (lon, lat).
- Demand pickle: `demand.pickle` is a dict keyed by ordered OD pairs (i, j) (direction matters). Values include tons_2025, tons_2030, …, tons_2050.

## Notebook patterns to follow (usage.ipynb)
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
- The notebook imports: pandas, requests, geopandas, shapely, matplotlib. Install these to run examples.
- No build system or tests in this repo; treat it as a data + notebook project.

## Gotchas and tips
- Edge keys (i, j) are undirected and normalized min→max; demand keys (i, j) are directed — don’t swap.
- Waterway nodes in README are also described in `intermodal-218.csv`; the notebook currently reads `intermodal-217.csv` for selected intermodal nodes. Prefer the notebook’s BASE_URL + filenames for programmatic access.
- An update on 2025‑01‑03 changed `W-adj.pickle` mode string to 'W' — don’t hardcode earlier assumptions.

## Where to start
- Open `usage.ipynb`, ensure the deps above are installed, run top→down. Use the helpers to load pickles and build GeoDataFrames.
- For quick examples, search the notebook for: `url_D`, `url_W`, `url_H`, `url_R`, and `create_geoframe_from_edges` to see concrete usage snippets.


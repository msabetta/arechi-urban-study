# Arechi Urban Study

Studio urbanistico del Piazzale Gipo Viani e Stadio Arechi (Salerno)

Obiettivi:
- modellazione 3D area
- analisi mobilità e spazi pubblici
- proposta di riqualificazione urbana

## Installation

```bash
git clone https://github.com/msabetta/arechi-urban-study.git
cd arechi-urban-study
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

The project is organized as follows:
- `analysis/`: Python scripts for land‑use analysis, GIS processing, etc.
- `scripts/`: Utility scripts such as 3D model generation.
- `notebooks/`: Jupyter notebooks that run the full workflow.
- `visualizations/`: Generated diagrams and maps.
- `data/`: Raw OSM extracts and auxiliary datasets.

To run the main notebook:
```bash
jupyter lab notebooks/urban_analysis.ipynb
```

## Data Sources

- OpenStreetMap extract for Salerno area (downloaded via `osmnx`).
- Local GIS layers for parking, stadium buffers, etc.

## Contributing

Feel free to open issues or submit pull requests. Follow the contribution guidelines in `CONTRIBUTING.md`.

## License

This project is licensed under the MIT License.
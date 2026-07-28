# Carbon Emissions and Climate Policy Tracker

Global carbon emissions and climate policy compliance tracker built on the Our World in Data CO2 dataset. Analyzes emissions trajectories, Paris Agreement alignment, and decarbonization progress. Built with Python, Pandas, Plotly, Matplotlib, and Flask.

## Overview

Tracked CO2 emissions across 50 largest emitters over a 10 year period using real data compiled from the Global Carbon Project, BP Statistical Review, and UNFCCC. Classified countries by Paris Agreement compliance status and identified decarbonization leaders. Delivered an executive dashboard with emissions trajectory charts and interactive global mapping.

## Results

| Metric | Value |
|--------|-------|
| Global CO2 (2024) | 38,598.58 Million Tonnes |
| Global CO2 Per Capita | 4.73 Tonnes |
| Ahead of Target | 9 countries (18%) |
| On Track | 17 countries (34%) |
| Critically Off Track | 11 countries (22%) |

## Key Findings

- Netherlands leads decarbonization with 4.23% annual intensity reduction
- Ukraine has the fastest absolute emissions decline at -4.89% CAGR
- China reduced carbon intensity by 2.33% annually despite 2.48% absolute growth
- No top 50 emitter achieved absolute decoupling (GDP growth with CO2 decline)

## Features

- Real data from Our World in Data covering 200+ countries
- 10-year emissions trajectory analysis (2015-2024)
- Paris Agreement compliance classification framework
- Decarbonization rate tracking by country
- Absolute decoupling identification
- 4-panel executive dashboard with dark theme
- Interactive Plotly choropleth emissions map
- Flask web application with country lookup and embedded charts

## Live Demo

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1H637wXDGrQ5kfLBBvA3zQZ6onFpu5IwQ?usp=sharing)

**Live Demo:** [https://carbon-emissions-tracker-38fa.onrender.com](https://carbon-emissions-tracker-38fa.onrender.com)

## Data Source

Our World in Data CO2 and Greenhouse Gas Emissions dataset, compiled from Global Carbon Project, BP Statistical Review of World Energy, and UNFCCC.

## Tech Stack

Python, Pandas, NumPy, Matplotlib, Plotly, Flask

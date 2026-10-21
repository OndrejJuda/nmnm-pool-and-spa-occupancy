# nmnm-pool-and-spa-occupancy

Sledování obsazenosti bazénu a wellness v [Městských lázních Nové Město na Moravě](https://lazne.nmnm.cz/).

GitHub Actions každých 15 minut (06:00–21:00 pražského času) stáhne tabulku návštěvnosti z `https://lazne.nmnm.cz/data/lazne/navstevnost-homepage.php` a připíše řádek do `data/YYYY-MM.csv`.

## Data

| Sloupec | Význam |
|---|---|
| `timestamp` | skutečný čas měření, Europe/Prague s offsetem |
| `weekday` | 1 = pondělí … 7 = neděle |
| `hour` | hodina měření (místní čas) |
| `areal` | celý areál |
| `bazen` | bazén |
| `fitness` | fitness |
| `wellness` | wellness (na webu „GWellness“) |
| `koupele`, `masaze`, `solarium` | ostatní oblasti |

Hodnota je okamžitý počet lidí uvnitř. Mimo provozní dobu jsou nuly — filtrovat až při analýze (provozní doba se liší podle dne a sezóny, viz [Provozní doba](https://lazne.nmnm.cz/provozni-doba/)).

## Spolehlivost

Plánované běhy GitHubu se zpožďují a občas vypadnou. Proto 15min interval a ukládání skutečného času. Kdyby výpadků bylo moc, workflow jde spouštět externě (např. cron-job.org) přes `workflow_dispatch`:

```
POST https://api.github.com/repos/OndrejJuda/nmnm-pool-and-spa-occupancy/actions/workflows/scrape.yml/dispatches
Authorization: Bearer <fine-grained PAT s Actions: write>
{"ref": "main"}
```

## Lokálně

```
python scrape.py
```

Jen standardní knihovna Pythonu 3.9+.

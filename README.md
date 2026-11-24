# nmnm-pool-and-spa-occupancy

Sledování obsazenosti bazénu a wellness v [Městských lázních Nové Město na Moravě](https://lazne.nmnm.cz/).

GitHub Actions workflow, spouštěný přes cron-job.org každých 15 minut (06:00–20:45 pražského času), stáhne návštěvnost z `https://lazne.nmnm.cz/data/lazne/navstevnost-homepage.php` a připíše řádek do `data/YYYY-MM.csv`.

## Data

| Sloupec | Význam |
|---|---|
| `timestamp` | skutečný čas měření, Europe/Prague s offsetem |
| `weekday` | 1 = pondělí … 7 = neděle |
| `hour` | hodina měření (místní čas) |
| `areal` | celý areál — od 23.11.2026 web neukazuje, prázdné |
| `bazen` | bazén |
| `fitness` | fitness |
| `wellness` | wellness |
| `koupele`, `masaze`, `solarium` | ostatní oblasti — od 23.11.2026 web neukazuje, prázdné |
| `stav` | čas „stav k“ z webu, kdy se počítadlo naposledy aktualizovalo (od 24.11.2026) |
| `stale` | 1 = web označil čísla jako zastaralá (od 24.11.2026) |

Hodnota je okamžitý počet lidí uvnitř. Mimo provozní dobu jsou nuly — filtrovat až při analýze (provozní doba se liší podle dne a sezóny, viz [Provozní doba](https://lazne.nmnm.cz/provozni-doba/)).

## Spolehlivost

Vestavěný `schedule` trigger GitHubu byl nepoužitelný (za ~24 h 4 běhy místo ~70, zpoždění přes hodinu), proto workflow spouští cron-job.org přes `workflow_dispatch`:

```
POST https://api.github.com/repos/OndrejJuda/nmnm-pool-and-spa-occupancy/actions/workflows/scrape.yml/dispatches
Authorization: Bearer <fine-grained PAT s Actions: write>
{"ref": "main"}
```

Token vyprší 20.01.2027 — pak je potřeba vygenerovat nový a vyměnit ho v cron-job.org.

## Lokálně

```
python scrape.py
```

Jen standardní knihovna Pythonu 3.9+.

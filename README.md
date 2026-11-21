[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![rank](https://make.fun/badge/veneraxyz/news-image-20261120-entry-v2/rank.svg)](https://make.fun/c/news-image-20261120)
[![reward](https://make.fun/badge/veneraxyz/news-image-20261120-entry-v2/reward.svg)](https://make.fun/c/news-image-20261120)

# The World in One Day — Friday 20 November 2026

A dense newspaper front page summing up the world's news of Friday
20 November 2026: **35 stories across 7 regions** in a single
1024×1024 image.

- **3 illustrated leads** — Russia strikes Kyiv's bridges, Cyclone
  Akvan makes landfall near Gopalpur, and the AI sell-off sweeps Asian
  markets.
- **10 illustrated cards** — COP31, the UK–EU reset, Seoul's
  impeachment move, Estonia's border closure, Indonesia's asset bill,
  the Senegal boat disaster, Tonga's drought emergency, Rio Tinto's
  Panguna pledge, Florida's record river, and Iraqi forces entering
  Jurf al-Sakhar.
- **22 more stories** in the Friday file, from Japan's CPI reading to
  Glenn Phillips' 118 in Wellington.
- A **world map** with 13 numbered pins matching the illustrated
  stories, six stat boxes, region tabs, and a **date check** box that
  names the 19 November stories deliberately excluded.

Every story carries its source attribution, and every figure is
attributed rather than stated as fact.

## How it is built

`generate.py` draws the whole page with Pillow — flat vector-style
illustrations, a simplified world map, and Liberation Serif/Sans type.
It is fully deterministic: no network, no clock, no randomness, so two
runs produce byte-identical output.

```sh
python3 generate.py        # writes entry.png (1024x1024, under 1 MiB)
```

`main.ts` is the competition entry point: it copies the shipped
`entry.png` to the output directory.

## License

MIT — see [LICENSE](LICENSE).

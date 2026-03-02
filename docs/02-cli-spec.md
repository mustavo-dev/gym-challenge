# CLI Spec (M1 MVP)

## cycle
- cycle create --cycle-id ... --name ... --start ... --end ... --tz Europe/Berlin
- cycle list
- cycle activate --cycle-id ...
- cycle close --cycle-id ...

## participant
- participant add --name "First Last"
- participant list
- participant deactivate --name "First Last"

## member
- member add --cycle-id ... --name "First Last"
- member remove --cycle-id ... --name "First Last"
- member list --cycle-id ...

## checkin
- checkin record --cycle-id ... --name "First Last" --points N [--at "YYYY-MM-DDTHH:MM"]
- checkin import --cycle-id ... --csv path.csv

## admin
- admin correct --cycle-id ... --name "First Last" --score-day YYYY-MM-DD --points N [--reason "..."]

## report
- report leaderboard --cycle-id ... --from YYYY-MM-DD --to YYYY-MM-DD
- report export --cycle-id ... --from ... --to ... --out out/leaderboard.csv
- report whatsapp --cycle-id ... --from ... --to ...

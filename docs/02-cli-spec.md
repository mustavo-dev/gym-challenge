# CLI Spec (M1 MVP)

## cycle

* cycle create --cycle-id ... --name ... --start-day YYYY-MM-DD ... --end-day YYYY-MM-DD ... --tz Europe/Berlin
* cycle list
* cycle activate --cycle-id ...
* cycle close --cycle-id ...

## participant

* participant add --name "Last, First"
* participant list
* participant deactivate --name "Last, First"

## member

* member add --cycle-id ... --name "Last, First"
* member remove --cycle-id ... --name "Last, First"
* member list --cycle-id ...

## checkin

* checkin record --cycle-id ... --name "Last, First" --points N \[--at "YYYY-MM-DDTHH:MM"]
* checkin import --cycle-id ... --csv path.csv

## admin

* admin correct --cycle-id ... --name "Last, First" --score-day YYYY-MM-DD --points N --reason "..."
* admin reactivate --cycle-id ... --name "Last, First" [--effective-day YYYY-MM-DD] --reason "..."
* admin apply-auto-inactive --cycle-id ... --through YYYY-MM-DD

## report

* report leaderboard --cycle-id ... --from YYYY-MM-DD --to YYYY-MM-DD
* report export --cycle-id ... --from ... --to ... --out out/leaderboard.csv
* report whatsapp --cycle-id ... --from ... --to ...

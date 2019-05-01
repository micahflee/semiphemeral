# Semiphemeral

_This project is a work in progress. It not ready to use yet._

There are plenty of tools that let you make your Twitter feed ephemeral, automatically deleting tweets older than some threshold, like one month. Semiphemeral does this, but also lets you automatically exclude tweets based on criteria: how many RTs or likes they have, and if they're part of a thread where one of your tweets has that many RTs or likes. It also lets you manually select tweets you'd like to exclude from deleting.

## Development

Make sure you have [pipenv](https://pipenv.readthedocs.io/en/latest/). Then install dependencies:

```sh
pipenv install --dev
```

And run the program like this:

```sh
pipenv run python ./app.py --help
```

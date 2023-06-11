# Build instructions

You need:

- Python 3
- Node.js

Install poetry deps:

```
poetry install
cd semiphemeral/frontend
npm install
cd ../..
```

Build the frontend:

```
poetry run build
```

Run Semiphemeral:

```
poetry run semiphemeral
```
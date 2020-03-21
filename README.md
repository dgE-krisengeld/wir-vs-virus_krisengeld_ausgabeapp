# WirVsVirus Krisengeld Ausgabeapp


Tools used:

- Python >= 3.7
- poetry
- Code style & linting:
  - Black
  - isort
  - mypy
  - flake8


How to setup a dev environment:
- Clone project
- Then run:
  ```shell 
  poetry install
  ```
- Now everything should be installed and you can run the app with
  ```shell
  poetry run dge-ausgabeapp
  ```

Apply codestyle (black, isort)
```
make format
```

Run linting:
```shell
make lint
```

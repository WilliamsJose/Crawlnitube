<h1 align="center"> Crawlnitube </h1>

<p align="center">Anitube Api scrapper</p>

### Api documentation

#### Latest animes released

```http
  GET /anime/latest?page={page number}
```

| Param         | Type       | Description                                |
| :------------ | :--------- | :----------------------------------------- |
| `page`        | `number`   | **Optional**. For navigation between pages |

#### Search for anime by name

```http
  GET /anime/search?name={anime name}
```

| Param        | Type       | Description                                              |
| :----------- | :--------- | :------------------------------------------------------- |
| `name`       | `string`   | **Required**. So you don't know what you want? Try latest |

#### Anime info like title, description, episodes, etc.

```http
  GET /anime/info?id={anime id or episode id}&page={page number}
```

| Param        | Type                 | Description                 |
| :----------- | :------------------- | :-------------------------- |
| `id`         | `string \| number`   | **Required**. to find       |

| Param        | Type       | Description                                 |
| :----------- | :--------- | :------------------------------------------ |
| `page`       | `number`   | **Optional**. For navigation between pages  |

#### Stream episode by id

```http
  GET /anime/stream?id={episode id}
```

| Param        | Type                 | Description                 |
| :----------- | :------------------- | :-------------------------- |
| `id`         | `number`             | **Required**. to stream     |



### Running

Clone repo

```bash
  git clone https://github.com/WilliamsJose/Crawlnitube.git
```

Go to created dir

```bash
  cd Crawlnitube
```
#### Local with python 3.11 or newest version

Install deps

```bash
  pip install -r requirements.txt
```

Start

```bash
  python app.py
```
#### With docker

Build

```bash
  sudo docker build -t crawlnitube .
```

And run

```bash
  docker run -p 4000:4000 --name crawlnitube crawlnitube:latest
```

#### With Kubernetes

if running on minikube, this could be of great help before the next commands: 
`eval $(minikube docker-env)`

```bash
  docker build -t crawlnitube:latest . && kubectl apply -f kubernetes/
```
<h1 align="center"> Crawlnitube </h1>

<p align="center">Anitube Api scrapper</p>

#### Some features
- [x] Get recent episodes
- [x] Search anime by name
  - [ ] ?Pagination for search
- [x] Get anime info by id or url
  - [ ] Pagination for episodes in anime info
- [x] Get Stream episode by id

#### Endpoints
- /anime/latest?page={page number}
- /anime/search?name={anime name}
- /anime/info?id={anime id or episode id}
- /anime/stream?id={episode id}

### TODO
- na /info trazer todos os eps do anime


-- notes, works on jsfiddle
<head>
  <link href="https://vjs.zencdn.net/8.6.1/video-js.css" rel="stylesheet" />

  <!-- If you'd like to support IE8 (for Video.js versions prior to v7) -->
  <!-- <script src="https://vjs.zencdn.net/ie8/1.1.2/videojs-ie8.min.js"></script> -->
</head>

<body>
  <video
    id="my-video"
    class="video-js"
    controls
    preload="auto"
    width="640"
    height="264"
    poster="https://www.anitube.vip/media/videos/tmb/280260/default.jpg"
    data-setup='{"controls": true, "autoplay": false, "preload": "auto"}'
  >
    <source src="http://127.0.0.1:4000/anime/stream?id=280260" type="video/mp4" />
    <!-- <source src="MY_VIDEO.webm" type="video/webm" /> -->
    <p class="vjs-no-js">
      To view this video please enable JavaScript, and consider upgrading to a
      web browser that
      <a href="https://videojs.com/html5-video-support/" target="_blank"
        >supports HTML5 video</a
      >
    </p>
  </video>

  <script src="https://vjs.zencdn.net/8.6.1/video.min.js"></script>
</body>
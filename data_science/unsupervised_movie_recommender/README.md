<a name="readme-top"></a>

<h1 align="center">
  <br>
  <img src="https://github.com/MichlF/projects/raw/main/data_science/unsupervised_movie_recommender/static/images/movie_clap.png" 
  title="Image taken from Flaticon: Those Icons" alt="From Flaticon Those Icons" width="75"></a>
  <br>
  Morpheus Movie Oracle
  <br>
</h1>

<h4 align="center">— A movie recommender website —</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#acknowledgements">Acknowledgements</a>
</p>

<p align="center">
    <a href="https://github.com/MichlF/projects/issues">Report Bug</a> •
    <a href="https://github.com/MichlF/projects/issues">Request Feature</a>
</p>

<p align="center">
    <br>
    <img src="https://github.com/MichlF/projects/blob/main/data_science/unsupervised_movie_recommender/static/images/website1.PNG?raw=True" alt="Snippet of website" width="500"/>
    <img src="https://github.com/MichlF/projects/blob/main/data_science/unsupervised_movie_recommender/static/images/website2.PNG?raw=True" alt="Snippet of website" width="500"/>
    <br>
</p>

## Key Features

* Recommends movies: randomly, based on non-negative matrix factorization or neighborhood-based collaborative filtering
* You can further filter any amount of recommendations by year, genre or average userbase rating

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## How To Use

For this app to work you can either just navigate to [this website](https://michlf.pythonanywhere.com/) [^1] or clone this repo onto your computer. Make sure to install the requirements from the `requirements.txt` file along with it.

Once you've ran the preprocessing script to obtain your base models, you can run the `app.py` file either from your IDE or the terminal:

```bash
python app.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing  

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

> [blog.michelfailing.de](https://blog.michelfailing.de) &nbsp;&middot;&nbsp;
> GitHub [@MichlF](https://github.com/MichlF) &nbsp;&middot;&nbsp;
> Twitter [@FailingMichel](https://twitter.com/FailingMichel)


[^1]: The website might be very slow due to the restrictions of PythonAnywhere's basic plan. Random recommender mode should work decently though.

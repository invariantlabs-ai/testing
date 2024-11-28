# Invariant Testing documentation

Documentation for the Invariant Testing. 

To locally serve a live version of the documentation, run the following command in this directory:

```bash
docker build -t invariant-docs .
docker run -it -p 8000:8000 -e DEV_MODE=true -v .:/docs/ invariant-docs 
```

With `DEV_MODE=true` and the mounted volume, the documentation will reflect changes made to the markdown files in real-time.

For deployment, we build the Docker image and push it to the registry:


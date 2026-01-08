# vibe-search

Music recommendation engine using CLAP (Contrastive Language-Audio Pretraining) embeddings. Finds sonically similar songs based on audio characteristics rather than metadata or genre tags.

<video src="demo.mp4" width="320" height="240" controls></video>

## Why AWS spot instances?

This is a stateless inference service, meaning all expensive computation (embedding generation) happens offline during the build phase. At runtime it is just loading precomputed vectors and doing cosine similarity.

If a spot instance gets reclaimed, Kubernetes reschedules the pod on a new node. For fault-tolerant, cost-sensitive workloads like this, spot instances provide considerable cost savings over on demand pricing.


## How it works

1. **Offline**: CLAP model processes audio files and generates 512-dimensional embeddings
2. **Build**: Embeddings are baked into the docker image (153KB  for 75 songs)
3. **Runtime**: API loads embeddings and computes cosine similarity

## API

```bash
# get all available songs
curl http://<ip>:30080/songs

# get recommendations for a song
curl -X POST http://<ip>:30080/recommend \
  -H "Content-Type: application/json" \
  -d '{"song": "IN THIS DARK", "top_k": 5}'
```

response:
```json
{
  "matched": "LEEAAV - IN THIS DARK",
  "recommendations": [
    {"song": "P Steve Officiel - Bebe go", "similarity": 0.907},
    {"song": "heiwr - Quatro Paredes", "similarity": 0.904},
    {"song": "Laurence DaNova - Real to Me", "similarity": 0.883}
  ]
}
```

## Deployment

**Prerequisites**: AWS CLI, Terraform, Docker, Kubectl

```bash
# precompute embeddings (local)
python scripts/precompute.py /path/to/audio/files

# build and push image
docker build -t yourusername/vibe-search:latest .
docker push yourusername/vibe-search:latest

# deploy infrastructure
cd infra
terraform init
terraform apply

# configure argocd to watch gitops repo
# (see vibe-search-gitops repo)
```

## Teardown

```bash
cd infra
terraform destroy
```

## Related Repos

- [vibe-search-gitops](https://github.com/Pike-Dzurny/vibe-search-gitops) - Includes the Kubernetes manifests for argocd

## Tech Stack

- **ML**: CLAP (laion/clap-htsat-unfused), scikit-learn
- **API**: FastAPI, uvicorn
- **Container**: Docker
- **Orchestration**: k3s (lightweight kubernetes)
- **Gitops**: ArgoCD
- **Infrastructure**: Terraform, AWS EC2 Spot Instances
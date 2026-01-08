# vibe-search

Music recommendation API deployed on a self-managed Kubernetes cluster (k3s) running on AWS EC2 Spot Instances, with GitOps-driven continuous deployment via ArgoCD. Uses CLAP (Contrastive Language-Audio Pretraining) embeddings to find sonically similar songs based on audio characteristics rather than metadata or genre tags. Infrastructure provisioned with Terraform and containerized with Docker.

https://github.com/user-attachments/assets/c8862485-3045-48cb-8405-0c15e9cc4073

## Why AWS spot instances?

This is a stateless inference service, meaning all expensive computation (embedding generation) happens offline during the build phase. At runtime it is just loading precomputed vectors and doing cosine similarity.

If a spot instance gets reclaimed, Kubernetes reschedules the pod on a new node. For fault-tolerant, cost-sensitive workloads like this, spot instances provide considerable cost savings over on demand pricing.


## How it works

A CLAP model processes audio files and generates 512-dimensional embeddings offline, which are then baked into the Docker image during the build phase, about 153KB for 75 songs. At runtime, the API simply loads these pre-computed embeddings and computes cosine similarity against incoming queries.

## API

```bash
# get all available songs
curl http://<ip>:30080/songs

# get recommendations for a song
curl -X POST http://<ip>:30080/recommend \
  -H "Content-Type: application/json" \
  -d '{"song": "IN THIS DARK", "top_k": 3}'
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

- [vibe-search-gitops](https://github.com/Pike-Dzurny/vibe-search-gitops) - Includes the Kubernetes manifests for ArgoCD

## Tech Stack

- **ML**: CLAP (laion/clap-htsat-unfused), scikit-learn
- **API**: FastAPI, uvicorn
- **Container**: Docker
- **Orchestration**: k3s (lightweight kubernetes)
- **Gitops**: ArgoCD
- **Infrastructure**: Terraform, AWS EC2 Spot Instances

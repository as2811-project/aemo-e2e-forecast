## End-to-end Time Series Forecasting
### Forecasting Electricity Demand and Retail Price using XGBoost and LSTM

This is an end-to-end ML/Time Series forecasting project. I'll be applying a few concepts from the book `Designing Machine Learning Systems` by Chip Huyen. 

**Motivation**

Online Machine Learning/Inference is fascinating to me. While it is fun to build a model locally and optimise it, you don't get to see how it would actually perform in the real world. There are so many 'gotchas' you'll encounter in production. It is important to know how to setup infra for your models, how to serve them, how often to retrain the models etc. This project will cover all these aspects of serving models (and some more).   

File Structure guide: 
- Jupyter Notebook files contain all prototyping and preprocessing code. This includes model building, evals, etc.
- `/api` will contain a FastAPI endpoint for inference [TODO]
- `/web` will contain code for the UI [TODO]

Stack:
- XGBoost
- PyTorch LSTM
- FastAPI
- Next.js
- Docker
- AWS
- Terraform
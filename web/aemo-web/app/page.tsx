/* eslint-disable react/no-unescaped-entities */
import PriceChart from "@/components/forecast";
import { Separator } from "@/components/ui/separator";
import ModelCard from "@/components/model-card";
import Image from "next/image";
import React from "react";

export default function Home() {
  return (
    <div className="tracking-tight text-justify">
      <main className="container max-w-3xl mx-auto px-4 py-12">
        <div className="mb-8 place-items-center">
          <h2 className="font-medium text-md text-neutral-400">
            Time Series Forecasting
          </h2>
          <h1 className="text-2xl font-semibold">
            <span className="bg-gradient-to-r from-green-600 via-cyan-500 to-sky-500 bg-clip-text text-transparent">
              Forecasting Electricity Prices with XGBoost
            </span>
          </h1>
          <h2 className="text-neutral-400 text-sm">Project, March-Apr 2025</h2>
        </div>
        <div className="items-center justify-center">
          <div className="flex items-center justify-between">
            <h1 className="font-medium">
              Electricity Price Forecasts for{" "}
              {new Date().toLocaleDateString("en-AU")}
            </h1>
            <button className="bg-green-600 hover:bg-green-700 text-white text-xs font-medium py-2 px-4 rounded-full ml-4">
              Simulate Price Spike
            </button>
          </div>
          <div>
            <PriceChart />
            <div>
              <label className="text-xs text-gray-500">
                Data source: Australian Energy Market Operator (AEMO)
              </label>
            </div>
            <Separator orientation="horizontal" className="mt-2 mb-4" />
            <ModelCard />
          </div>
        </div>
        <div className="mt-5">
          <h1 className="font-medium">Motivation</h1>
          <p>
            The motivation behind this project is to implement real world MLOps
            practices in a simple and easy to understand way. This project is a
            demonstration of how to build a simple time series forecasting model
            using XGBoost and how to train and deploy it using AWS Lambda, API
            Gateway and Glue/PySpark. A more complex model, based on
            Transformers, is in the works. This will be deployed using
            SageMaker, however, this will only be available to view in the
            GitHub repository and will not be a part of this application (due to
            the costs associated with running a SageMaker instance 🥲). The
            'Simulate Price Spike' button does not do much. It simply triggers
            an in-app notification letting the user know when to expect a price
            spike and adjust their usage accordingly. This is inpired by Amber
            Electric's work in this space.
          </p>
          <Separator className="mt-5 mb-5" />
          <h1 className="font-medium">Data</h1>
          <p>
            The Australian Energy Market Operator (AEMO) provides a
            comprehensive dashboard for electricity prices in Australia. This
            dashboard provides a range of data, including historical prices,
            demand, generation and more. The data used to train the XGBoost
            model is the historical electricity prices for the state of
            Victoria. The data is available{" "}
            <a
              className="text-blue-500"
              href="https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data"
            >
              here
            </a>
            . On top of this, their dashboards send data in 5 (Actuals) and 30
            minute (Forecasts) intervals. This data is used to make predictions,
            albeit not real time. I am unsure if this is allowed, so I will not
            be sharing the exact API endpoint.
          </p>
          <Separator className="mt-5 mb-5" />
          <h1 className="font-medium">XGBoost Fundamentals</h1>
          <p>
            XGBoost is a popular machine learning library that is used to build
            gradient boosting models. It is known for its speed and performance
            and is widely used in the industry. You might wonder, "Gee Anandh,
            why not use something like SARIMA or a more complex model like a
            Transformer?" A team that won a hackathon I participated in used
            XGBoost for a similar forecasting problem. This was intriguing as my
            understanding at the time was that boosters were not suitable for
            extrapolation. I decided to investigate this further and found that
            XGBoost can indeed be used for time series forecasting, but with
            some additional work.
          </p>
          <p className="mt-5">
            Unlike traditional time series models (e.g., ARIMA, Prophet),
            XGBoost does not explicitly account for time dependencies. Instead,
            it has to treat the forecasting problem as a regression task, where
            past observations are used as features to predict future values.
            Adding lag features, rolling features and exogenous features can
            help the model learn the time dependencies in the data.
          </p>
          <p className="mt-5">
            So what actually happens when you provide input data for inference?
            The model identifies which features are most informative for making
            predictions. XGBoost constructs multiple decision trees, where each
            node splits based on a condition (e.g., "Is RRP_t-1 greater than
            100?"). Instead of making a single prediction, XGBoost sequentially
            refines its estimates by correcting errors made by previous trees.
            Each new tree focuses on reducing the residual error from the
            previous iterations. After passing through multiple trees, the final
            prediction is obtained by combining the contributions from all
            trees.
          </p>
          <Separator className="mt-5 mb-5" />
          <h1 className="font-medium">Architecture</h1>
          <div className="p-4 items-center justify-center">
            <Image
              src={"/high-level.svg"}
              alt="Architecture"
              width={700}
              height={400}
            />
          </div>
          <label className="text-xs text-gray-500">System Architecture</label>
          <p className="mt-5">
            What you're seeing here is a high-level view of the architecture. It
            looks quite simple but the underlying logic took a lot of work and
            iterations. There are 4 Lambda functions that bring this system
            together. "Daily Data", as the name suggests, is part of the
            pipeline that fetches the last 24 hours' data and stores it in the
            landing zone in an S3 bucket. "Forecasts" is the function that
            handles inference. It takes data from the 5 days, transforms it as
            the input for the model (adds time-related features like hour of the
            day, day of the week etc. and a lag feature (t-1)), concats an empty
            data frame with just the features mentioned earlier along with
            future dates and predicts the RRP for those future dates. The
            forecasts are then written to a DynamoDB table, which is effectively
            used as a cache.
          </p>
          <p className="mt-5">
            There's a function called 'Server' which serves the cached
            predictions. I'm caching predictions to avoid running the Forecasts
            function for every request. It requires double the default memory
            allocation for a Lambda and takes a few seconds to perform all the
            necessary computations. So, to ensure the best possible user
            experience, I felt the need to add a caching layer.
          </p>
          <p className="mt-5">
            The last function is the 'Train' function which handles 'continuous'
            training. I train the model using its checkpoints weekly once. This
            is done to ensure that the model is up to date with the latest data.
            This is to ensure the model is up to date to handle data
            distribution shifts. A government policy introducing price caps
            could alter how supply and demand influence electricity prices, even
            if seasonal demand patterns remain the same (Concept Shift) or a
            major energy crisis could fuel price spikes, or geopolitical events
            could lead to sudden changes in electricity pricing behavior
            (Temporal Shift). While scenarios like this are infrequent,
            continuous training is still a good practice. This particular form
            of continuous training is also called Stateful Training. This allows
            us to train the model with fewer samples and still achieve good
            results.
          </p>
          <p className="mt-5">
            As for the data itself, a Glue job is triggered every week to
            transform data from the last 7 days and add all the features
            necessary to convert this into a supervised learning task (which is
            necessary for training a tree based model for forecasting). These
            components come together to form a simple yet effective system for
            forecasting electricity prices.
          </p>
          <Separator className="mt-5 mb-5" />
          <h1 className="font-medium">
            IaC and Continuous Delivery/Deployment
          </h1>
          <p>
            Setting up CI/CD is fairly simple for a project like this. The
            Lambda functions are container based and hence, the workflow builds
            an image, pushes it to a private ECR repository and updates the
            Lambda functions through the AWS CLI.
          </p>
          <p className="mt-5">
            CD for the Glue job is also setup in a similar in a similar way. For
            local development, I used the Glue Docker image from AWS to test the
            PySpark script. Setting this up with PyCharm on Mac was a bit tricky
            as the only tutorial I found online was for Windows. PyCharm's MacOS
            UI seems to be significantly different from the Windows UI but it is
            not too difficult to figure out. The workflow is setup to push the
            script to my S3 bucket and update the Glue job through the AWS CLI.
          </p>
          <p className="mt-5">
            For setting up the infrastructure, I used Terraform. It is somewhat
            overkill to use Terraform to setup an S3 bucket, DynamoDB table and
            a few IAM policies but I wanted to get some practice with it. If you
            plan on recreating (a part of) the infrastructure, it will be fairly
            easy to do so once you initialise Terraform in your environment.
          </p>
          <Separator className="mt-5 mb-5" />
          <h1 className="font-medium">Performance</h1>
          <p>
            In terms of execution times, the system performs well but of course,
            ideally you'd want an always-on service like an EC2 instance serving
            the model rather than a stateless service like Lambda. The forecasts
            function takes the longest to execute whilst requiring the highest
            amount of resources compared to the others. 256MB of memory does
            suffice but it could become a problem as the model's size grows with
            continual training.
          </p>
          <p className="mt-5">
            The model itself is quite performant. It gets an RMSE of around
            25-30 and an R² of ~0.80. This is not bad for a simple model like
            this. The model is trained on over 20,320 samples and uses 6
            features. The features are the RRPs of the previous day, the hour of
            the day, the day of the week, the month of the year, the day of the
            month and the year. Ideally, more exogenous data should be used but
            this is a good start.
          </p>
          <Separator className="mt-5 mb-5" />
          <h1 className="font-medium">Learnings</h1>
          <p>
            I always knew that model building was just a small part of the whole
            process, but I did not expect it to be this small. A lot of work
            goes into making the model accessible as an endpoint. Additionally,
            there are a lot of things to consider when it comes to
            infrastructure. For instance, I chose serverless for this project as
            I specifically wanted to implement a batch inference pipeline with a
            simple model. Ideally, this would be a more complex model that does
            real-time or frequent batch inferencing. So for my use case, Lambda
            functions work well. However, if I were to use a more complex model,
            I would consider using Sagemaker or an GPU-powered EC2 instance to
            help run frequent batch/real-time inference.
          </p>
          <p className="mt-5">
            According to Chip Huyen (author of the book 'Designing Machine
            Learning Systems'), ML engineering and MLOps is more Software
            Engineering/DevOps than Data Science. I, with my limited
            professional experience in the field, can confirm this. Automating
            the continual training and inference process required setting up
            components like Step Functions, Schedulers etc. I began this project
            2.5-3 weeks ago and a large chunk of this went towards architecting
            and engineering the system to make the model accessible.
          </p>
          <p className="mt-5">
            In conclusion, this project was a fun and challenging experience.
            I'm glad I read the Designing ML Systems book as I was able carry a
            lot of the insights from the book into this project. I highly
            recommend it!
          </p>
        </div>
      </main>
    </div>
  );
}

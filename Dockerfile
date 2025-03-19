FROM public.ecr.aws/lambda/python:3.12

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY pipeline/lambda/pipeline_lambda.py ${LAMBDA_TASK_ROOT}

CMD [ "pipeline_lambda.lambda_handler" ]
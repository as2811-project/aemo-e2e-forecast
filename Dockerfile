FROM public.ecr.aws/lambda/python:3.12

ARG DEFAULT_S3_BUCKET
ARG DEFAULT_DDB_TABLE

ENV S3_BUCKET=$DEFAULT_S3_BUCKET
ENV DDB_TABLE=$DEFAULT_DDB_TABLE

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
COPY pipeline/lambda/ ${LAMBDA_TASK_ROOT}/

CMD [ "pipeline_lambda.lambda_handler" ]
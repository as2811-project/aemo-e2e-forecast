FROM public.ecr.aws/lambda/python:3.12

ARG DEFAULT_S3_BUCKET
ARG DEFAULT_DDB_TABLE
ARG DEFAULT_API_URL

ENV S3_BUCKET=${DEFAULT_S3_BUCKET}
ENV DDB_TABLE=${DEFAULT_DDB_TABLE}
ENV API_URL=${DEFAULT_API_URL}

RUN echo "S3_BUCKET=${S3_BUCKET}" >> ${LAMBDA_TASK_ROOT}/.env && \
    echo "DDB_TABLE=${DDB_TABLE}" >> ${LAMBDA_TASK_ROOT}/.env && \
    echo "API_URL=${API_URL}" >> ${LAMBDA_TASK_ROOT}/.env

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
COPY pipeline/lambda/ ${LAMBDA_TASK_ROOT}/

CMD [ "pipeline_lambda.lambda_handler" ]

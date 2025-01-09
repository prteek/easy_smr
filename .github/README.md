# easy_smr
Easing Sagemaker Ops for R projects

**Credits**: This Project borrows heavily from [Sagify](https://github.com/Kenza-AI/sagify). It's a great project do check it out specially if you want to work with LLMs on Sagemaker.

---
Offers following commands to help work with Sagemaker

```text
Commands:
  build  Command to build SageMaker app
  cloud  Commands for AWS operations: upload data, train and deploy
  init   Command to initialize SageMaker template
  local  Commands for local operations: train and deploy
  push   Command to push Docker image to AWS ECR
```

## Installation
```shell
pip install easy-smr
```

## Getting help
```shell
easy_smr --help

```
And similarly for any sub commands `easy_smr cloud --help`

## Usage
`Note: It is assumed that AWS cli is setup and an AWS profile defined for the app to use. This profile would be required when initialising easy_smr` [See](https://github.com/prteek/easy_smr/tree/main?tab=readme-ov-file#aws-setup)

There are 5 broad steps to initialise build and test any project
1. Initialise easy_smr in the repository where code lives. Follow the prompts after running the `init` command
```shell
easy_smr init
```

2. Copy the relevant code in either `easy_smr_base/processing` or `easy_smr_base/training` or `easy_smr_prediction` folder

3. Build and Push Docker image with all the code and dependency (this is where `easy_smr` shines)
```shell
easy_smr build -a app-name
easy_smr push -a app-name
```
The Dockerfile that is used here is located at `app-name/easy_smr_base/Dockerfile`.
So any additional dependencies can be introduced in this file.

4. Test locally
```shell
easy_smr local process -f file.py -a app-name
```
Similarly there are commands for training a model or running a pipeline defined in a Makefile

5. Deploy/Run on Sagemaker
```shell
easy_smr cloud process -f file.py -a app-name -r $SAGEMAKER_EXCUTION_ROLE -e ml.t3.medium
```

## Features

### Model training
**easy_smr** enables seamless transition from local environment to training models on Sagemaker. Additionally such trained models could be deployed to a serverless endpoint!. A serverless endpoint can be very useful to have from cost and scale perspective. This avoids having to deploy a lambda function etc. for inference.

#### Getting started local training
##### Dependencies
First of all an *renv.lock* that captures all dependencies for training code is required. This needs to be maintained (and updated) in `app-name/easy_smr_base` as you develop the code. (See [renv](https://rstudio.github.io/renv/reference/index.html)). <br/>
The central idea around dependencies is that a single *renv* is used for a given project (placed automatically at `app-name/easy_smr_base` when the project is initialised) and that all the R scripts load and use this *renv*. <br/>
A simple way to use it in scripts is

```r
library(this.path)
library(renv)
load(here("..")) # Since renv location is one level up from all processing/training scripts

```
`A major assumption the package makes is that the working directory is where the project was initialised and from where *easy_smr* commands are run (i.e. directory where app-name.json file lives). It is also assumed that inside of scripts *here* (from this.path) is used load correct *renv* and source relevant files. This not being the case, Docker will fail to run the scripts properly.`

Additionally a *Dockerfile* in *app-name/easy_smr_base/Dockerfile* can be modified for flexibility in how the container is built.

##### Code
The code for training needs to be copied in **app-name/easy_smr_base/training/training.R** under the function *train_function* with any import statements at the top of the file. (Making sure path to renv is correctly specified at the top)
e.g.
```r
library(this.path)
library(renv)
load(here("..")) # Notice that renv is located just one level up any processing/training scripts
# Import other libraries after this

train_function <- function(input_data_path, model_save_path) {
    # The function to execute the training.

    # Args:
    #   input_data_path: [character], input directory path where all the training file(s) reside in
    #   model_save_path: [character], directory path to save your model(s)

    # TODO: Write your modeling logic (including loading data)
    mpg <- read.csv(paste(input_data_path, "mpg.csv", sep = "/"))

    lmod <- lm(mpg ~ horsepower + weight, mpg)
    print(summary(lmod))

    # TODO: save the model(s) under 'model_save_path'
    saveRDS(lmod, paste(model_save_path, "mpg_model.rds", sep = "/"))
}

```

##### Data
With the code and dependencies out of the way, a small sample of test data needs to be places at **app-name/easy_smr_base/local_test/test_dir/input/data/training**

For this example the dataset used is at https://raw.githubusercontent.com/plotly/datasets/master/auto-mpg.csv

##### Prepare container
Last step before training is preparing the container to include all dependencies, code and data
```shell
easy_smr build -a app-name
```

##### Train
With all this out of the way training can be started *easily*

```shell
easy_smr train -a app-name
```

This runs the training code inside the container so rest assured if everything worked here, it should work on Sagemaker

#### Getting started cloud training
##### AWS Setup
There are primarily 2 things required from AWS side
1. AWS Profile with credentials that can enable permissions to work with ECR, Sagemaker and S3.
This is specified in *~/.aws/config* file like following, along with accompanying set of credentials in *~/.aws/credentials* file

```text
[profile dev]
aws_account_id = 10987654321
region = eu-west-1
output = json
```

2. Sagemaker execution role to run training and processing jobs. This is generally of the form *arn:aws:iam::10987654321:role/AVMSagemakerExecutionRole* and it will be referred to as the variable *$SAGEMAKER_EXECUTION_ROLE* in the doumentation.

Additionally, specify a trust relationship for the user (relevant for profile) to assume the Sagemaker execution role.

This is done by adding the following json blob to Trust entities under Trust relationship tab of the role in IAM console. Any number of users can be added within the Statement field.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::109876543210:user/dev",
                "Service": "sagemaker.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

##### Push to ECR
If the container was built properly during local training it can be pushed to ECR *easily*
```shell
easy_smr push -a app-name
```

##### Data in S3
The dataset to train on needs to be present in s3. There is a command for copying local files to s3 *easily*
```shell
easy_smr cloud upload-data -i training_data.csv -s s3://bucket/folder/input -r $SAGEMAKER_EXECUTION_ROLE -a app-name
```

##### Train
Once the data and ECR image are in place invoking training is *easy*
```shell
easy_smr cloud train -n training-job -r $SAGEMAKER_EXECUTION_ROLE -e ml.m5.large -i s3://bucket/folder/input -o s3://bucket/folder/train/artefacts -a app-name
```
**Note**: that using *folder* as a parent leads us to nicely organise training data for the project. The folder can be anything, brownie points if it is name of the app.

##### Outputs
The training job writes text output in the console that can be useful for further steps in the pipeline
```text
Training on SageMaker succeeded
Model S3 location: s3://bucket/folder/train/artefacts/training-job-2024-08-07-10-41-23-345/output/model.tar.gz
```

This points to the location where model is saved and this text string can be used to extract model location and deploy the model.

It is often useful to also save this output in a text file.
```shell
easy_smr cloud train -n training-job -r $SAGEMAKER_EXECUTION_ROLE -e ml.m5.large -i s3://bucket/folder/input -o s3://bucket/folder/train/artefacts -a app-name | tee train_output.txt
```

### Model deployment

#### Getting started with local deployment

##### Code
To run inference using trained model
1. Model must be loaded in the container
2. Any input data must be handled and pre processed
3. Predictions made and output data processed if necessary

The code to accomplish all this needs to be defined in **app-name/easy_smr_base/prediction/plumber.R**. By default *text/csv* inputs are supported and results returned as *text/csv* but other formats can be introduced in the *serve* file. If the default settings are usable then the only changes to the code need to be in *model_fn* and *input_fn* along with any dependencies at the top. A sample code looks like following

```r
library(this.path)
library(renv)
load(here(".."))

# TODO load more libraries here if needed


# TODO Define a function to load the model to be used for predictions
model_fn <- function(model_save_path) {
    model <- readRDS(paste(model_save_path, "mpg_model.rds", sep = "/"))
    return(model)
}

# TODO Define a prediction function
predict_fn <- function(X, model) {
    # Here you would use your actual model to make predictions
    # Additionally any preprocessing required on X before prediction (X is an un-named matrix as it comes in)
    colnames(X) <- c("weight", "horsepower")
    predictions <- predict(model, X)
    return(predictions)
}

```

##### Deploy
Having setup the code, it is required to rebuild the container with updated serving code and run a local training job
```shell
easy_smr build -a app-name
easy_smr train -a app-name
```

This will create a model and place it in an appropriate directory where serving code can locate it.
Local serving is *easy*
```shell
easy_smr local deploy -a app-name
```

And it can be tested by passing the payload
```shell
curl -X POST \
http://localhost:8080/invocations \
-H 'Cache-Control: no-cache' \
-H 'Content-Type: text/csv' \
-d '4732.0,193.0
3302.0,88.0'


curl -X POST \
http://localhost:8080/invocations \
-H 'Cache-Control: no-cache' \
-H 'Content-Type: text/csv' \
-T payload.csv
```


#### Getting started with cloud deployment
After the container is updated with serving code it needs to be pushed to ECR and a cloud training step needs to be run to generate a model object

```shell
easy_smr push -a app-name
easy_smr cloud train -n training-job -r $SAGEMAKER_EXECUTION_ROLE -e ml.m5.large -i s3://bucket/folder/input -o s3://bucket/folder/train/artefacts -a app-name >| train_output.txt

```

To begin with the model location is required for deployment. It can either be manually provided or if you saved the entire output of training job to the *train_output.txt* file, the model location can be extracted and passed to depolyment commands.

```shell
easy_smr cloud deploy-serverless -s 2048 -n endpoint-name -r $SAGEMAKER_EXECUTION_ROLE -m s3://bucket/folder/train/artefacts/training-job-2024-08-07-10-41-23-345/output/model.tar.gz -a app-name
```

Serverless is the only option supported currently.

Extracting model location from training output file can be done by `$(grep -o -E "s3://[^ ]+" train_output.txt)`.

This is particularly useful when running these commands on a remote runner like Github actions. Training and deployment steps can be successively run without manual intervention.
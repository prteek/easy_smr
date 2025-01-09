library(this.path)
library(renv)
load(here(".."))

# TODO load more libraries here if needed


# TODO Define a function to load the model to be used for predictions
model_fn <- function(model_save_path) {
    # Load model object

    return(model)
}

# TODO Define a prediction function
predict_fn <- function(X, model) {
    # Here you would use your actual model to make predictions
    # Additionally any preprocessing required on X before prediction (X is an un-named matrix as it comes in)

    return(predictions)
}

#* Ping to show server is alive
#* @get /ping
function() {
    return("")
}

#* Parse input and return prediction from model
#* @param req The http request sent
#* @post /invocations
function(req, res) {
    # Get the content type from the request
    content_type <- req$HTTP_CONTENT_TYPE

    # Check if the content type is 'text/csv'
    if (content_type == "text/csv") {
        # Read the raw input data
        input_data <- req$postBody

        # Use read.csv to read the CSV data into a data frame
        X <- read.csv(text = input_data, header = FALSE)

        # Load model
        prefix <- "/opt/ml"
        model_save_path <- paste(prefix, "model", sep = "/")
        model <- model_fn(model_save_path)

        # Make predictions
        predictions <- predict_fn(X, model)

        # Collapse the result into a single string
        out <- paste(predictions, collapse = "\n")

        # Return the results as CSV in the response
        res$status <- 200
        res$setHeader("Content-Type", "text/csv")
        res$body <- out
        return(res)
    } else {
        # If the content type is unsupported, return an error response
        res$status <- 400
        res$body <- "Unsupported content type"
        return(res)
    }
}

library(here)
library(renv)

# TODO add renv path here to load it (replace first part with app name)
load(here("replace_with_project_directory", "easy_smr_base"))

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

#' Ping to show server is alive
#' @get /ping
function() {
    return("")
}

#' Parse input and return prediction from model
#' @param req The http request sent
#' @post /invocations
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

        # Convert the predictions to a data frame
        output <- data.frame(results = predictions)
        colnames(output) <- NULL
        # Convert the data frame back to CSV format
        out <- paste(capture.output(write.csv(output, row.names = FALSE)), collapse = "\n")

        # Return the results as a CSV in the response
        return(list(response = out, status = 200, mimetype = "text/csv"))
    } else {
        # If the content type is unsupported, return an error response
        res$status <- 400
        return(list(error = "Unsupported content type"))
    }
}

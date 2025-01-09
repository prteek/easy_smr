#!/usr/bin/env bash
# Order of operations is important since when invoked from sagemaker for serving no argument is passed
# For training, train argument is passed by default from sagemaker
# 'process' and 'make' are handled differently by overriding entrypoint during job definitions in Sagemaker
if [ $1 = "train" ]; then
    Rscript $TARGET_DIR/easy_smr_base/training/train
elif [ $1 = "process" ]; then
    Rscript $TARGET_DIR/easy_smr_base/processing/$2
elif [ $1 = "make" ]; then
    cd $TARGET_DIR/easy_smr_base/processing
    make $2
else # This case is reserved for serving for compatibility with Sagemaker
    Rscript $TARGET_DIR/easy_smr_base/prediction/serve
fi
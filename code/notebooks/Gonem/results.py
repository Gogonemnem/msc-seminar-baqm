import tensorflow as tf
import pandas as pd
import numpy as np


def monte_carlo_dropout(x, model, n_samples=10, postproc=None, return_weight=False):
    weights = []
    preds = []
    for i in range(n_samples):
        weight = model.attention_layer(x, return_weights=True, training=True)[1]
        pred = model(x, training=True)
        if postproc is not None:
            pred = postproc(pred)
        preds.append(pred)
        weights.append(weight)
    
    if return_weight:
        return np.stack(preds), np.stack(weights)
    return np.stack(preds)



def weight_results(weights, columns):
    intermediate_dict = {}
    weights_dict = {}
    
    features  = columns.get_level_values(0).unique()
    countries = columns.get_level_values(1).unique()
    
    for weight, column in zip(weights, columns):
        intermediate_dict[column] = weight.numpy()

    for country in countries:
        if 'country' not in weights_dict:
            weights_dict['country'] = [country]
        else:
            weights_dict['country'].append(country)

        for feature in features:
            w = intermediate_dict.get((feature, country), np.nan)
            if feature not in weights_dict:
                weights_dict[feature] = [w]
            else:
                weights_dict[feature].append(w)


    weights = pd.DataFrame.from_dict(weights_dict)
    return weights


def forecast_interval(data, alpha):
    # assumption that the different samples are on the first dimension
    lb = np.percentile(data, q=alpha, axis=0)
    ub = np.percentile(data, q=1-alpha, axis=0)
    return tf.stack([lb, ub], axis=0)
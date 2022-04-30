import os
import indicators
import start_trading as dtMain

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd


subfolderModels = "./BinanceModels/"


def saveAccuracyToFile(df, accuracyTotal, ticker, timeframe):
    path = subfolderModels+'Acuracy_'+timeframe+'.csv'
    df_new = pd.DataFrame([[ticker, df.loc['Up']['precision'], df.loc['Down']['precision'], accuracyTotal]], columns = ["TICKER", "UP", "DOWN", "TOTAL"])
    if not os.path.exists(path):
        df_new.to_csv(path)
    else:
        df_new.to_csv(path, mode='a', header=False)
    

def buildRandomForestModel(df, ticker, timeframe):
    # To calculate indicators we need to calculate the change in price from one period to the next. To do this, we will use the diff() method. Grab the close column and call the diff() method. 
    # The diff() method will calculate the difference from one row to the next.
    df['Price_change'] = df['Close'].diff()

    # Calculate percentage change * 100x leverage to adjust it for targeted gain
    df['Price_change_%'] = df['Close'].pct_change() * 100 * 100

    # Create filter conditios so in Column 'Price_change_%_final' 1.0 represents gain > targetGain, -1.0 represents gain < -targetGain and 0.0 neutral gain not important to us
    filterUp = (df['Price_change_%']>dtMain.targetGain)
    filterDown = (df['Price_change_%']<-dtMain.targetGain)
    df['Price_change_%_final'] = np.where(filterUp, 1.0, 0.0)
    filterNeutral = (df['Price_change_%_final']==0.0)
    df['Price_change_%_final'] = np.where(filterDown, -1.0, np.where(filterNeutral, 0.0, 1.0))

    close_groups = df['Close']
    close_groups = close_groups.transform(lambda x : np.sign(x.diff()))
    df['Prediction'] = close_groups

    #df['Prediction'] = np.where(df['Prediction']==0.0, 0.0, 1.0) ??
    #df.loc[df['Prediction'] == 0.0] = 1.0  OLD

    df['RSI'] = indicators.rsi(df)
    df['STOCH'] = indicators.stoch(df)
    df['Williams'] = indicators.williams(df)
    df['MACD'] = indicators.macd(df)
    df['ROC'] = indicators.roc(df)
    df['OBV'] = indicators.obv(df)
    df['ADX'] = indicators.adx(df)
    df['CMF'] = indicators.cmf(df)

    df = df.dropna()    # Remove NaN rows

    #print(df.dtypes)

    ################################### RandomForestClassifier ###################################

    # Grab our X & Y Columns.
    X = df[dtMain.indicatorsToUse]
    Y = df['Prediction']

    # We now split the data to see how good our decision tree is performing
    X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state = 0, test_size=0.2, stratify = Y)


    # Create a Random Forest Classifier
    rand_frst_clf = RandomForestClassifier(n_estimators = 100, oob_score = True, criterion = "gini", random_state = 0)

    # Fit the data to the model
    rand_frst_clf.fit(X_train.values, y_train)

    # Make predictions
    y_pred = rand_frst_clf.predict(X_test.values)

    

    # Print the Accuracy of our Model.
    accuracyTotal = accuracy_score(y_test, y_pred, normalize = True) * 100.0
    print('\nCorrect RandomForestClassifier Prediction (%): ', accuracyTotal)
    """ The accuracy_score function computes the accuracy, either the fraction (default) or the count (normalize=False) of correct predictions. 
    Accuracy is defined as the number of accurate predictions the model made on the test set. Imagine we had three TRUE values [1, 2, 3], and our model predicted the 
    following values [1, 2, 4] we would say the accuracy of our model is 66 %. """
    # Define the traget names
    target_names = ['Down', 'Neutral', 'Up']

    # Build a classifcation report
    report = classification_report(y_true = y_test, y_pred = y_pred, target_names = target_names, output_dict = True)

    # Add it to a data frame, transpose it for readability.
    report_df = pd.DataFrame(report).transpose()
    print(report_df)
    #saveAccuracyToFile(report_df, accuracyTotal, ticker, timeframe)
    """ Now the fun part, interpretation. When it comes to evaluating the model, there we generally look at the accuracy. If our accuracy is high, it means our model is correctly classifying items.
    In some cases, we will have models that may have low precision or high recall. It's difficult to compare two models with low precision and high recall or vice versa. To make results 
    comparable, we use a metric called the F-Score. The F-score helps to measure Recall and Precision at the same time. It uses Harmonic Mean in place of Arithmetic Mean by punishing the 
    extreme values more."""
    # Calculate feature importance and store in pandas series
    feature_imp = pd.Series(rand_frst_clf.feature_importances_, index=X.columns).sort_values(ascending=False)
    print(feature_imp)

    # See the tree
    """ dot_data_rf = StringIO()
    data_rf = tree.export_graphviz(rand_frst_clf.estimators_[99], filled=True, feature_names=indicatorsToUse, out_file=dot_data_rf, class_names=target_names)
    graphviz.Source(data_rf)
    
    graph_rf = pydotplus.graph_from_dot_data(dot_data_rf.getvalue())
    graph_rf.write_pdf('RandomForest.pdf') """

    return rand_frst_clf
    ################################### RandomForestClassifier ###################################

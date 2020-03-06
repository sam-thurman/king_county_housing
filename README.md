# Relation of Home Prices to Home Features using King County Data

# Process
 Our process started off with each of the three group members individually exploring the data.
For example, what did certain column names of the data mean or how was the data represented (numbers vs text)?
After this initial exploration, our group came together to figure out what our working dataset should contain.
According to the requirements of the project, our data should only contain housing data from 2019.
This single file of data is what we having been working from in order to find the best correlations possible.

# Methodology
Trial and error has been our main method of trying to find what features from our data correlate to higher home prices.
The specific way in which our group has been trying to find these relationship is by using a Logistic Regression model.
One issue we have had to watch out for while using the Logistic Regression model is something called Multicollinearity.
Testing for low multicollinearity scores, maximum of 5, is straightforward and documented in our group's code.
Please note that a maximum score of 5 was set by our group and not a de facto standard to always use.
To determine a strong correlation, between home feature(s) and home price, from the Logistic Regression model our group has been using the R-squared value.
The closer to 1 the stronger the correlation, this is harder to find given that we have to account for the maximum multicollinearity score between various house features.

# Findings
Our base Logistic Regression model had an R-squared value of 0.343. In trying to predict possible home sale prices for this base model, our group only used one home feature - Total Square Feet. 

After some more work and exploration, we came up with a somewhat better optimized model. This model had an R-squared value of 0.422. This time our group included an additional 12 home features with the original home feature of Total Square Feet. 

The final model our group came up with received an R-squared value of 0.435. It includes a total of 7 home features to predict home sale price. All three of the models shared here did not have any features that crossed the multicollinearity threshold of 5, that our group set.

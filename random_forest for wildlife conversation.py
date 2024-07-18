import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data=pd.read_csv('wildlife.csv')
data.head()
fraction_to_keep = 0.025 
df_sampled = data.sample(frac=fraction_to_keep, random_state=42)

from sklearn.preprocessing import StandardScaler
import pandas as pd

# Select numerical columns
numerical_columns = df_sampled.select_dtypes(include=['float64', 'int64']).columns
# Separate the numerical data
numerical_data = df_sampled[numerical_columns]
# Standardization (Z-score Scaling)
standard_scaler = StandardScaler()
scaled_data = standard_scaler.fit_transform(numerical_data)

# Create a new DataFrame with scaled data
scaled_df = pd.DataFrame(scaled_data, columns=numerical_columns)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor

# Assuming df is your DataFrame and target_columns contains the names of target variables
target_columns = ['Lion_KD500', 'Buffalo_KD500', 'Bushbuck_KD500', 'Caracal_KD500','Cheetah_KD500','Duiker_KD500','Eland_KD500','Elephant_KD500','Gemsbok_KD500','Giraffe_KD500','Hippo_KD500','Impala_KD500','Jackal_KD500','Kudu_KD500','Leopard_KD500','Reedbuck_KD500','Roan_KD500','Sable_KD500','SHyena_KD500','Steenbok_KD500','Warthog_KD500','Waterbuck_KD500','Wildcat_KD500','Wilddog_KD500','Wildebeest_KD500','Zebra_KD500']

# Separate features (X) and target variables (y)
X = scaled_df.drop(target_columns, axis=1) # Assuming other columns are features
y = scaled_df[target_columns]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Standardize the features (optional but often beneficial)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Drop rows with missing values
X_train_cleaned = X_train.dropna()
y_train_cleaned = y_train.loc[X_train_cleaned.index]

from sklearn.ensemble import RandomForestRegressor
# Create a Random Forest regressor
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
# Train the regressor
rf_regressor.fit(X_train, y_train)
# Make predictions
predictions = rf_regressor.predict(X_test)
print(predictions)

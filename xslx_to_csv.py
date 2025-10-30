import pandas as pd

input_path = "D:\Code\Python\VSCode\VisualizationLearning\data\long_format_yearly_price.xlsx"
output_path = "D:\Code\Python\VSCode\VisualizationLearning\data\long_format_yearly_price.csv"

df = pd.read_excel(input_path)
df.to_csv(output_path, index=False)
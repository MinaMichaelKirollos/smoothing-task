# Carino Smoothing

## Usage

Install requirements
```
pip install -r requirements.txt
```
Instantiate CarinoMethod with an args dictionary and call .smooth()

Example args:
```python
args = {"period_selection": "Q", "factor_selection": ""}
```
See FactorSelection and PeriodSelection for allowed values

Example usage:
```python
(CarinoMethod(args).smooth()).to_csv("final.csv")
```


## Assumptions
* I have assumed that factor return is just the raw return for a factor given single time period, in the provided Carino smoothing formula F is a matrix, I have assumed that when considering a single factor F is not a matrix as I think the performance of another factor should not be relevent when calculating the performance of a single factor
* I have assumed that in the formula for multi-period adjustment, R is the multi-period return as defined above that uses single period return
* I could not reproduce the results of the 2nd table in the word document which shows the smoothed outputs using the formulas provided. I have taken the provided formulas as a source of truth going forward.

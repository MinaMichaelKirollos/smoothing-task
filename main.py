import enum
from typing import Dict, Optional

import numpy as np
import pandas as pd


class FactorSelection(enum.Enum):
    NONE = ""
    AUSTRALIA = "Australia"
    AUSTRIA = "Austria"
    BELGIUM = "Belgium"
    DENMARK = "Denmark"
    FINLAND = "Finland"
    FRANCE = "France"
    FUTURES = "Futures"
    GERMANY = "Germany"
    HUNGARY = "Hungary"
    IRELAND = "Ireland"
    ITALY = "Italy"
    NETHERLANDS = "Netherlands"
    NORWAY = "Norway"
    OTHERS = "Others"
    POLAND = "Poland"
    PORTUGAL = "Portugal"
    SPAIN = "Spain"
    SWEDEN = "Sweden"
    SWITZERLAND = "Switzerland"
    UNITED_KINGDOM = "United Kingdom"
    UNITED_STATES = "United States"


class PeriodSelection(enum.Enum):
    NONE = ""
    QUARTERLY = "Q"
    YEARLY = "Y"
    INCEPTION_TO_DATE = "I"


class CarinoMethod:
    def __init__(self, args: Optional[Dict] = None) -> None:
        self.returns = self._extract_transform().fillna(np.nan).replace(0, np.nan)
        self._verify_apply_args(args)

    def _verify_apply_args(self, args: Optional[Dict]):
        if args:
            assert (
                args["period_selection"] in PeriodSelection
                and args["factor_selection"] in FactorSelection
            )
            if args["factor_selection"]:
                self.returns = self.returns.loc[[args["factor_selection"]]]
            if args["period_selection"]:
                self.period_selection = args["period_selection"]
            else:
                self.period_selection = PeriodSelection.INCEPTION_TO_DATE
        else:
            self.period_selection = PeriodSelection.NONE

    def _extract_transform(self) -> pd.DataFrame:
        returns = (
            pd.read_excel("data/CodingTestData.xlsx")
            .pivot_table(index="COUNTRY", columns="REF_DATE", values="TOTAL")
            .rename_axis("FACTOR", axis=0)
        )
        return returns

    def _multi_period_return(self, single_return: pd.Series) -> float:
        """Applies multi period return using a series of returns"""
        return (1 + single_return).prod() - 1

    def _single_period_adjustment(self, single_returns: pd.Series) -> pd.Series:
        """Applies single period adjustment to every value in a Series"""
        return np.log(1 + single_returns) / single_returns

    def _multi_period_adustment(self, multi_period_return: float) -> float:
        """Applies the multi period adjustment using multi period return"""
        return np.log(multi_period_return + 1) / multi_period_return

    def _smooth_factor(
        self,
        factor_row: pd.Series,
    ) -> pd.Series:
        """Returns the smoothed values for a single factor, calls the appropriate functions to return the
        single period adjustment for the chosen factor and the multiperiod adjustment for that factor
        """
        single_adjustment_row = self._single_period_adjustment(factor_row)
        multi_period_return = self._multi_period_return(factor_row)
        multi_period_adjustment = self._multi_period_adustment(multi_period_return)
        result = (single_adjustment_row * factor_row) / multi_period_adjustment
        return result

    def smooth(self) -> pd.DataFrame:
        self.returns.columns = pd.to_datetime(self.returns.columns)
        match self.period_selection:
            case PeriodSelection.QUARTERLY.value:
                quarterly_returns = self.returns.resample("Q", axis=1).sum()
                smoothed_quarterly = quarterly_returns.apply(
                    self._smooth_factor, axis=1
                )
                smoothed_quarterly.columns = [
                    f"smoothed_{col.year}-Q{col.quarter}"
                    for col in quarterly_returns.columns
                ]
                self.returns = pd.concat([self.returns, smoothed_quarterly], axis=1)
            case PeriodSelection.YEARLY.value:
                yearly_returns = self.returns.resample("Y", axis=1).sum()
                smoothed_yearly = yearly_returns.apply(self._smooth_factor, axis=1)
                smoothed_yearly.columns = [
                    f"smoothed_{col.year}" for col in yearly_returns.columns
                ]
                self.returns = pd.concat([self.returns, smoothed_yearly], axis=1)
            case PeriodSelection.INCEPTION_TO_DATE.value:
                self.returns["inception_to_date"] = self.returns.apply(
                    lambda x: self._smooth_factor(x).sum(), axis=1
                )
        return self.returns


if __name__ == "__main__":
    args = {"period_selection": "Q", "factor_selection": ""}
    (CarinoMethod(args).smooth()).to_csv("final.csv")

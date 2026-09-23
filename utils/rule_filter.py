import pandas as pd

def filter_rules(rules_df: pd.DataFrame, min_support: float = 0.0, min_confidence: float = 0.0, min_lift: float = 0.0) -> pd.DataFrame:
    """
    Filter a pandas DataFrame of association rules based on support, confidence, and lift thresholds.
    
    Args:
        rules_df: DataFrame containing the association rules (must have 'support', 'confidence', 'lift' columns).
        min_support: Minimum support threshold.
        min_confidence: Minimum confidence threshold.
        min_lift: Minimum lift threshold.
        
    Returns:
        Filtered DataFrame.
    """
    if rules_df is None or rules_df.empty:
        return rules_df
        
    filtered = rules_df.copy()
    
    if min_support > 0:
        filtered = filtered[filtered['support'] >= min_support]
        
    if min_confidence > 0:
        filtered = filtered[filtered['confidence'] >= min_confidence]
        
    if min_lift > 0:
        filtered = filtered[filtered['lift'] >= min_lift]
        
    return filtered

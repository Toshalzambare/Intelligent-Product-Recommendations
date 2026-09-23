import joblib
import pandas as pd
import os

class RecommenderSystem:
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.rules = None
        self.frequent_itemsets = None
        self.products = []
        self.load_models()

    def load_models(self):
        try:
            rules_path = os.path.join(self.models_dir, 'association_rules.pkl')
            itemsets_path = os.path.join(self.models_dir, 'frequent_itemsets.pkl')
            mapping_path = os.path.join(self.models_dir, 'product_mapping.pkl')

            if os.path.exists(rules_path):
                self.rules = joblib.load(rules_path)
            
            if os.path.exists(itemsets_path):
                self.frequent_itemsets = joblib.load(itemsets_path)
                
            if os.path.exists(mapping_path):
                self.products = joblib.load(mapping_path)
            
            print(f"Loaded {len(self.rules) if self.rules is not None else 0} rules.")
        except Exception as e:
            print(f"Warning: Could not load models. {e}")

    def get_products(self):
        """Return a list of all available products."""
        return self.products

    def recommend(self, selected_products, min_confidence=0.0, min_lift=0.0):
        """
        Generate recommendations based on a list of selected products.
        """
        if self.rules is None or self.rules.empty:
            return []

        # Convert input to a frozen set for comparison
        selected_set = frozenset(selected_products)

        # Filter rules where antecedents are a subset of the selected products
        # We want rules where the user has selected ALL the antecedents.
        # Alternatively, we could just look for rules where antecedents intersect the selected products.
        # Let's find rules where antecedents are a subset of selected_products
        matching_rules = self.rules[self.rules['antecedents'].apply(lambda x: x.issubset(selected_set))]

        # Apply user filters
        if min_confidence > 0:
            matching_rules = matching_rules[matching_rules['confidence'] >= min_confidence]
        if min_lift > 0:
            matching_rules = matching_rules[matching_rules['lift'] >= min_lift]

        if matching_rules.empty:
            return []

        # Extract consequents
        recommendations = []
        for _, row in matching_rules.iterrows():
            for item in row['consequents']:
                # Ensure we don't recommend items the user already selected
                if item not in selected_set:
                    recommendations.append({
                        "product": item,
                        "confidence": float(row['confidence']),
                        "lift": float(row['lift']),
                        "support": float(row['support'])
                    })

        # Sort recommendations by confidence, then lift
        recommendations = sorted(recommendations, key=lambda x: (x['confidence'], x['lift']), reverse=True)

        # Deduplicate recommendations, keeping the one with the highest confidence
        seen = set()
        deduped = []
        for rec in recommendations:
            if rec['product'] not in seen:
                seen.add(rec['product'])
                deduped.append(rec)

        return deduped

    def get_all_rules(self):
        """Return all rules as a list of dicts for the explorer UI."""
        if self.rules is None:
            return []
            
        rules_list = []
        for _, row in self.rules.iterrows():
            rules_list.append({
                "antecedents": list(row['antecedents']),
                "consequents": list(row['consequents']),
                "support": float(row['support']),
                "confidence": float(row['confidence']),
                "lift": float(row['lift'])
            })
        return rules_list
        
    def get_analytics(self):
        """Return summary statistics."""
        return {
            "total_products": len(self.products),
            "total_rules": len(self.rules) if self.rules is not None else 0,
            "frequent_itemsets": len(self.frequent_itemsets) if self.frequent_itemsets is not None else 0
        }

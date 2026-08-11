"""
Acquisition Sourcing - Pandas-based Data Processor (v2.0)
Upgraded with hard filters, value creation levers, ownership criteria, and business model detection.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import re

# Column name mapping: Spanish → English
COLUMN_MAPPING = {
    "Nombre": "Company_Name",
    "Código NIF": "Tax_ID",
    "Provincia": "Province",
    "Localidad": "City",
    "Calle": "Street",
    "Código postal": "Postal_Code",
    "Forma jurídica detallada": "Legal_Form",
    "Dirección web": "Website",
    "Teléfono": "Phone",
    "Fecha constitución": "Founding_Date",
    "Código primario CNAE 2009": "CNAE_Code",
    "Literal código CNAE 2009 primario": "CNAE_Description",
    "Descripción actividad": "Activity_Description",
    "Ultimo año disponible": "Last_Year_Available",
    "Indicator de\nIndependencia BvD": "Independence_Indicator",
    "Independencia BvD": "Independence_Indicator",
    "Nombre auditor": "Auditor_Name",
    "Número de accionistas": "Shareholder_Count",
    "Accionista - Tipo": "Shareholder_Type",
    "GUO - Nombre": "GUO_Name",
    "ISH - Nombre": "ISH_Name",
    "Núm. de empresas en el grupo corporativo": "Group_Company_Count",
    "Número empleados\nÚlt. año disp.": "Employee_Count",
    "Número empleados Últ. año disp.": "Employee_Count",
    "Cash flow\nmil EUR\nÚlt. año disp.": "Cashflow_Current",
    "Cash flow mil EUR Últ. año disp.": "Cashflow_Current",
    "Deudas a largo plazo\nmil EUR\nÚlt. año disp.": "LT_Debt_Current",
    "Deudas a largo plazo mil EUR Últ. año disp.": "LT_Debt_Current",
    "Ingresos de explotación\nmil EUR\nÚlt. año disp.": "Revenue_Current",
    "Ingresos de explotación mil EUR Últ. año disp.": "Revenue_Current",
    "Ingresos de explotación\nmil EUR\nAño - 1": "Revenue_Y1",
    "Ingresos de explotación mil EUR Año - 1": "Revenue_Y1",
    "Ingresos de explotación\nmil EUR\nAño - 2": "Revenue_Y2",
    "Ingresos de explotación mil EUR Año - 2": "Revenue_Y2",
    "EBITDA\nÚlt. año disp.": "EBITDA_Current",
    "EBITDA Últ. año disp.": "EBITDA_Current",
    "EBITDA\nAño - 1": "EBITDA_Y1",
    "EBITDA Año - 1": "EBITDA_Y1",
    "EBITDA\nAño - 2": "EBITDA_Y2",
    "EBITDA Año - 2": "EBITDA_Y2",
}

# Hard filter thresholds
HARD_FILTERS = {
    "ebitda_min_eur": 1_000,      # €1M minimum
    "ebitda_max_eur": 5_000,      # €5M maximum
    "ebitda_margin_min": 0.05,    # 5% minimum (soft guideline)
    "debt_to_ebitda_max": 4.0,    # 4x maximum
    "max_years_negative": 1,      # Allow max 1 year negative EBITDA
}

# Business model keywords (B2B, Recurring, Project-based)
B2B_KEYWORDS = ['b2b', 'b-b', 'empresas', 'businesses', 'distribución', 'distribution', 
                'mayorista', 'wholesale', 'industrial', 'manufacturing', 'servicios empresa']
RECURRING_KEYWORDS = ['suscripción', 'subscription', 'mantenimiento', 'maintenance', 'servicio',
                     'recurrente', 'recurring', 'contrato', 'contract', 'asistencia', 'support']
PROJECT_KEYWORDS = ['proyecto', 'project', 'consultoría', 'consulting', 'obra', 'construction',
                   'asesoría', 'advisory', 'puntual']

# Value creation levers thresholds
VALUE_CREATION_LEVERS = {
    "professionalization": {
        "description": "Replace founder/family with systems/processes",
        "indicators": ["founder_led", "owner_age", "no_professional_mgmt"]
    },
    "revenue_growth": {
        "description": "Unlock stagnant top-line",
        "indicators": ["low_cagr", "market_share_gap", "geographic_expansion"]
    },
    "margin_expansion": {
        "description": "Remove inefficiencies/personal expenses",
        "indicators": ["low_margin", "high_opex", "supplier_consolidation"]
    },
    "buy_and_build": {
        "description": "Consolidation platform in fragmented market",
        "indicators": ["fragmented_market", "acquisition_targets", "sme_heavy"]
    },
    "pricing_power": {
        "description": "Raise prices in under-priced business",
        "indicators": ["cost_plus_pricing", "high_demand", "low_switching_cost"]
    },
    "customer_concentration": {
        "description": "Reduce reliance on top 3 customers",
        "indicators": ["customer_concentration", "sticky_contracts"]
    },
    "digital_transformation": {
        "description": "Modernize legacy operations",
        "indicators": ["manual_processes", "paper_based", "legacy_tech"]
    }
}


class AcquisitionDataProcessor:
    """Process SABI data with hard filters, value creation levers, and ownership analysis."""
    
    def __init__(self, excel_file="20260122 1812, 4646, 4652, 7732, 8130.xlsx", sheet_name="Data"):
        """Initialize processor and load data."""
        self.excel_file = excel_file
        self.sheet_name = sheet_name
        self.raw_df = None
        self.derived_df = None
        self.output_df = None
        self.hard_filter_results = {}
        
    def load_raw_data(self):
        """Load and translate Data sheet."""
        print(f"Loading '{self.sheet_name}' sheet from {self.excel_file}...")
        
        self.raw_df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name)
        
        # Clean column names
        self.raw_df.columns = self.raw_df.columns.str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
        
        print(f"  Loaded {len(self.raw_df)} rows")
        
        # Map Spanish to English
        rename_dict = {}
        for spanish, english in COLUMN_MAPPING.items():
            spanish_clean = spanish.replace('\n', ' ').replace('\r', ' ').strip()
            for col in self.raw_df.columns:
                if col.strip() == spanish_clean:
                    rename_dict[col] = english
                    break
        
        self.raw_df.rename(columns=rename_dict, inplace=True)
        
        # Convert date columns
        date_cols = ["Founding_Date", "Last_Year_Available"]
        for col in date_cols:
            if col in self.raw_df.columns:
                try:
                    self.raw_df[col] = pd.to_datetime(self.raw_df[col], errors='coerce')
                except:
                    pass
        
        # Convert numeric columns
        numeric_cols = [
            "Employee_Count", "Cashflow_Current", "LT_Debt_Current",
            "Revenue_Current", "Revenue_Y1", "Revenue_Y2",
            "EBITDA_Current", "EBITDA_Y1", "EBITDA_Y2",
            "Shareholder_Count", "Group_Company_Count"
        ]
        for col in numeric_cols:
            if col in self.raw_df.columns:
                self.raw_df[col] = pd.to_numeric(self.raw_df[col], errors='coerce')
        
        # Remove rows with no company name
        self.raw_df = self.raw_df[self.raw_df['Company_Name'].notna()].reset_index(drop=True)
        
        print(f"✓ Data loaded and translated to English")
        print(f"✓ {len(self.raw_df)} companies ready for processing\n")
        
        return self.raw_df
    
    def calculate_derived_metrics(self):
        """Calculate all derived metrics."""
        print("Calculating derived metrics...")
        
        self.derived_df = self.raw_df.copy()
        
        # EBITDA Margin %
        self.derived_df['EBITDA_Margin_%'] = np.where(
            (self.derived_df['EBITDA_Current'].notna()) & 
            (self.derived_df['Revenue_Current'].notna()) &
            (self.derived_df['Revenue_Current'] != 0),
            self.derived_df['EBITDA_Current'] / self.derived_df['Revenue_Current'],
            np.nan
        )
        
        # Cashflow Margin %
        self.derived_df['Cashflow_Margin_%'] = np.where(
            (self.derived_df['Cashflow_Current'].notna()) & 
            (self.derived_df['Revenue_Current'].notna()) &
            (self.derived_df['Revenue_Current'] != 0),
            self.derived_df['Cashflow_Current'] / self.derived_df['Revenue_Current'],
            np.nan
        )
        
        # FCF to EBITDA Conversion (using Cashflow as proxy for FCF)
        self.derived_df['FCF_to_EBITDA_Conversion_%'] = np.where(
            (self.derived_df['Cashflow_Current'].notna()) & 
            (self.derived_df['EBITDA_Current'].notna()) &
            (self.derived_df['EBITDA_Current'] > 0),
            (self.derived_df['Cashflow_Current'] / self.derived_df['EBITDA_Current']),
            np.nan
        )
        
        # EBITDA per Employee
        self.derived_df['EBITDA_per_Employee'] = np.where(
            (self.derived_df['EBITDA_Current'].notna()) & 
            (self.derived_df['Employee_Count'].notna()) &
            (self.derived_df['Employee_Count'] != 0),
            self.derived_df['EBITDA_Current'] / self.derived_df['Employee_Count'],
            np.nan
        )
        
        # Revenue CAGR 3Y
        self.derived_df['Revenue_CAGR_3Y_%'] = np.where(
            (self.derived_df['Revenue_Current'].notna()) & 
            (self.derived_df['Revenue_Y2'].notna()) &
            (self.derived_df['Revenue_Y2'] > 0),
            (np.power(self.derived_df['Revenue_Current'] / self.derived_df['Revenue_Y2'], 1/2) - 1),
            np.nan
        )
        
        # EBITDA CAGR 3Y
        self.derived_df['EBITDA_CAGR_3Y_%'] = np.where(
            (self.derived_df['EBITDA_Current'].notna()) & 
            (self.derived_df['EBITDA_Y2'].notna()) &
            (self.derived_df['EBITDA_Y2'] > 0),
            (np.power(self.derived_df['EBITDA_Current'] / self.derived_df['EBITDA_Y2'], 1/2) - 1),
            np.nan
        )
        
        # Years of Consecutive Positive EBITDA
        def count_positive_ebitda(row):
            count = 0
            if pd.notna(row['EBITDA_Current']) and row['EBITDA_Current'] > 0:
                count += 1
                if pd.notna(row['EBITDA_Y1']) and row['EBITDA_Y1'] > 0:
                    count += 1
                    if pd.notna(row['EBITDA_Y2']) and row['EBITDA_Y2'] > 0:
                        count += 1
            return count if count > 0 else np.nan
        
        self.derived_df['Years_Positive_EBITDA'] = self.derived_df.apply(count_positive_ebitda, axis=1)
        
        # Debt to EBITDA
        self.derived_df['Debt_to_EBITDA'] = np.where(
            (self.derived_df['LT_Debt_Current'].notna()) & 
            (self.derived_df['EBITDA_Current'].notna()) &
            (self.derived_df['EBITDA_Current'] != 0),
            self.derived_df['LT_Debt_Current'] / self.derived_df['EBITDA_Current'],
            np.nan
        )
        
        # Company Age (years)
        self.derived_df['Company_Age_Years'] = np.where(
            self.derived_df['Founding_Date'].notna(),
            (datetime.now() - self.derived_df['Founding_Date']).dt.days / 365.25,
            np.nan
        ).astype(float)
        
        print(f"✓ Derived metrics calculated\n")
        
        return self.derived_df
    
    def detect_business_model(self):
        """Detect business model type (B2B, Recurring, Project-based)."""
        print("Detecting business models...")
        
        def classify_business_model(row):
            text = str(row.get('Activity_Description', '') or '') + " " + str(row.get('CNAE_Description', '') or '')
            text_lower = text.lower()
            
            is_b2b = any(keyword in text_lower for keyword in B2B_KEYWORDS)
            is_recurring = any(keyword in text_lower for keyword in RECURRING_KEYWORDS)
            is_project = any(keyword in text_lower for keyword in PROJECT_KEYWORDS)
            
            if is_recurring and not is_project:
                return "RECURRING"
            elif is_project and not is_recurring:
                return "PROJECT_BASED"
            elif is_recurring and is_project:
                return "MIXED"
            else:
                return "UNCLEAR"
        
        self.derived_df['Business_Model'] = self.derived_df.apply(classify_business_model, axis=1)
        
        def classify_b2b_b2c(row):
            text = str(row.get('Activity_Description', '') or '') + " " + str(row.get('CNAE_Description', '') or '')
            text_lower = text.lower()
            
            is_b2b = any(keyword in text_lower for keyword in B2B_KEYWORDS)
            return "B2B" if is_b2b else "B2C/OTHER"
        
        self.derived_df['Market_Type'] = self.derived_df.apply(classify_b2b_b2c, axis=1)
        
        print(f"✓ Business models classified\n")
    
    def detect_ownership_structure(self):
        """Detect founder/family ownership, hidden groups, and multi-entity structures."""
        print("Detecting ownership structures...")
        
        # Step 1: Normalize and extract shareable identifiers
        self.derived_df['_shareholder_normalized'] = self.derived_df['GUO_Name'].fillna('').astype(str).str.lower().str.strip()
        self.derived_df['_phone_cleaned'] = (
            self.derived_df['Phone'].fillna('').astype(str)
            .str.replace(r'[\s\-\+34]', '', regex=True)
            .str.lower()
            .str.strip()
        )
        self.derived_df['_website_domain'] = (
            self.derived_df['Website'].fillna('').astype(str)
            .str.lower()
            .str.extract(r'((?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,})', expand=False)
        )
        self.derived_df['_address_key'] = (
            self.derived_df['Street'].fillna('').astype(str) + '|' +
            self.derived_df['Postal_Code'].fillna('').astype(str) + '|' +
            self.derived_df['City'].fillna('').astype(str)
        ).str.lower().str.strip()
        
        # Step 2: Count occurrences of each signal
        shareholder_counts = self.derived_df[self.derived_df['_shareholder_normalized'] != ''].groupby('_shareholder_normalized').size()
        phone_counts = self.derived_df[self.derived_df['_phone_cleaned'] != ''].groupby('_phone_cleaned').size()
        website_counts = self.derived_df[self.derived_df['_website_domain'].notna()].groupby('_website_domain').size()
        address_counts = self.derived_df[self.derived_df['_address_key'] != '|'].groupby('_address_key').size()
        
        # Step 3: Create binary flags for shared signals (≥2 occurrences)
        self.derived_df['FLAG_SHARED_SHAREHOLDER'] = (
            self.derived_df['_shareholder_normalized'].map(shareholder_counts).fillna(1) >= 2
        ).astype(int)
        
        self.derived_df['FLAG_SHARED_PHONE'] = (
            self.derived_df['_phone_cleaned'].map(phone_counts).fillna(1) >= 2
        ).astype(int)
        
        self.derived_df['FLAG_SHARED_WEBSITE'] = (
            self.derived_df['_website_domain'].map(website_counts).fillna(1) >= 2
        ).astype(int)
        
        self.derived_df['FLAG_SHARED_ADDRESS'] = (
            self.derived_df['_address_key'].map(address_counts).fillna(1) >= 2
        ).astype(int)
        
        # Step 4: Calculate GROUP_SIGNAL_SCORE (0-10)
        self.derived_df['GROUP_SIGNAL_SCORE'] = (
            3 * self.derived_df['FLAG_SHARED_SHAREHOLDER'] +
            3 * self.derived_df['FLAG_SHARED_PHONE'] +
            3 * self.derived_df['FLAG_SHARED_WEBSITE'] +
            1 * self.derived_df['FLAG_SHARED_ADDRESS']
        ).clip(upper=10)  # Cap at 10
        
        # Step 5: FLAG_HIDDEN_GROUP = High signal + VC/PE keywords
        def detect_hidden_group(row):
            # If no group signals, it's independent
            if row['GROUP_SIGNAL_SCORE'] == 0:
                return "No"
            
            # Check for VC/PE/Corporate financial ownership
            guo = str(row.get('GUO_Name', '') or '').lower()
            ish = str(row.get('ISH_Name', '') or '').lower()
            shareholder_type = str(row.get('Shareholder_Type', '') or '').lower()
            
            vc_pe_keywords = [
                'venture', 'private equity', 'fondo', 'fund', 'capital', 'inversión',
                'investment', 'société', 'portfolio', 'partners', 'spv', 'shell',
                'equity', 'holdings' #(without family context)
            ]
            
            combined_text = guo + " " + ish + " " + shareholder_type
            has_financial = any(kw in combined_text for kw in vc_pe_keywords)
            
            # If group signals exist + financial ownership = hidden group
            if has_financial and row['GROUP_SIGNAL_SCORE'] > 0:
                return "Yes"
            
            # If high group signal (≥6) but no financial keywords = domestic group/consolidation
            # Still flag as "Yes" because multi-entity structure needs investigation
            if row['GROUP_SIGNAL_SCORE'] >= 6:
                return "Yes"
            
            return "No"
        
        self.derived_df['FLAG_Hidden_Group'] = self.derived_df.apply(detect_hidden_group, axis=1)
        
        # Identify VC/PE/Corporate parent keywords
        def detect_financial_owner(row):
            guo = str(row.get('GUO_Name', '') or '').lower()
            ish = str(row.get('ISH_Name', '') or '').lower()
            shareholder_type = str(row.get('Shareholder_Type', '') or '').lower()
            
            vc_pe_keywords = ['venture', 'private equity', 'fondo', 'fund', 'capital', 'inversión',
                            'holdings', 'investment', 'société', 'ag', 'gmbh', 'ltd', 'portfolio']
            
            has_vc_pe = any(kw in guo + ish + shareholder_type for kw in vc_pe_keywords)
            
            return "VC/PE/CORP" if has_vc_pe else "Family/Founder"
        
        self.derived_df['Ownership_Type'] = self.derived_df.apply(detect_financial_owner, axis=1)
        
        # Shareholder concentration (fewer = better for acquisition)
        self.derived_df['Shareholder_Concentration'] = np.where(
            self.derived_df['Shareholder_Count'].notna(),
            np.where(self.derived_df['Shareholder_Count'] <= 3, "HIGH", 
                    np.where(self.derived_df['Shareholder_Count'] <= 5, "MEDIUM", "LOW")),
            "UNKNOWN"
        )
        
        # Succession risk (owner age > 55 is typical risk threshold)
        self.derived_df['Succession_Risk'] = "NO_DATA"
        
        # Clean up temporary columns
        temp_cols = ['_shareholder_normalized', '_phone_cleaned', '_website_domain', '_address_key']
        self.derived_df.drop(columns=temp_cols, inplace=True)
        
        print(f"✓ Ownership structures classified")
        print(f"  - Shared Shareholder: {self.derived_df['FLAG_SHARED_SHAREHOLDER'].sum()} companies")
        print(f"  - Shared Phone: {self.derived_df['FLAG_SHARED_PHONE'].sum()} companies")
        print(f"  - Shared Website: {self.derived_df['FLAG_SHARED_WEBSITE'].sum()} companies")
        print(f"  - Shared Address: {self.derived_df['FLAG_SHARED_ADDRESS'].sum()} companies")
        print(f"  - Hidden Groups Detected: {(self.derived_df['FLAG_Hidden_Group'] == 'Yes').sum()} companies\n")
    
    def apply_hard_filters(self):
        """Apply critical exclusion filters."""
        print("Applying hard filters...")
        
        self.derived_df['HARD_FILTER_PASS'] = True
        self.derived_df['HARD_FILTER_FAILURES'] = ""
        
        failures = []
        
        # Filter 1: VC/PE/International parent exclusion (only if VC/PE + high group signal)
        has_financial_parent = (
            (self.derived_df['Ownership_Type'] == "VC/PE/CORP") &
            (self.derived_df['GROUP_SIGNAL_SCORE'] >= 6)
        )
        
        self.derived_df.loc[has_financial_parent, 'HARD_FILTER_PASS'] = False
        self.derived_df.loc[has_financial_parent, 'HARD_FILTER_FAILURES'] += "VC/PE Parent (Multi-Entity) | "
        failures.append(("VC/PE/Corporate Parent (Multi-Entity)", has_financial_parent.sum()))
        
        # Filter 2: EBITDA range (€1-5M)
        ebitda_out_of_range = (
            (self.derived_df['EBITDA_Current'].isna()) |
            (self.derived_df['EBITDA_Current'] < HARD_FILTERS['ebitda_min_eur']) |
            (self.derived_df['EBITDA_Current'] > HARD_FILTERS['ebitda_max_eur'])
        )
        
        self.derived_df.loc[ebitda_out_of_range, 'HARD_FILTER_PASS'] = False
        self.derived_df.loc[ebitda_out_of_range, 'HARD_FILTER_FAILURES'] += "EBITDA Out of Range | "
        failures.append(("EBITDA Outside €1-5M", ebitda_out_of_range.sum()))
        
        # Filter 3: Debt to EBITDA (max 4x)
        high_debt = (
            (self.derived_df['Debt_to_EBITDA'].notna()) &
            (self.derived_df['Debt_to_EBITDA'] > HARD_FILTERS['debt_to_ebitda_max'])
        )
        
        self.derived_df.loc[high_debt, 'HARD_FILTER_PASS'] = False
        self.derived_df.loc[high_debt, 'HARD_FILTER_FAILURES'] += f"High Debt (>{HARD_FILTERS['debt_to_ebitda_max']}x) | "
        failures.append(("High Debt (>4x EBITDA)", high_debt.sum()))
        
        # Filter 4: Project-based revenue (not recurring)
        project_based = self.derived_df['Business_Model'] == "PROJECT_BASED"
        
        self.derived_df.loc[project_based, 'HARD_FILTER_PASS'] = False
        self.derived_df.loc[project_based, 'HARD_FILTER_FAILURES'] += "Project-Based Revenue | "
        failures.append(("Project-Based Business (Low Predictability)", project_based.sum()))
        
        # Filter 5: Consecutive negative EBITDA
        years_negative = 3 - self.derived_df['Years_Positive_EBITDA']
        years_negative = years_negative.fillna(3)
        too_many_negative = years_negative > HARD_FILTERS['max_years_negative']
        
        self.derived_df.loc[too_many_negative, 'HARD_FILTER_PASS'] = False
        self.derived_df.loc[too_many_negative, 'HARD_FILTER_FAILURES'] += "Persistent Negative EBITDA | "
        failures.append(("Persistent Negative EBITDA", too_many_negative.sum()))
        
        passed = self.derived_df['HARD_FILTER_PASS'].sum()
        total = len(self.derived_df)
        
        print(f"\nHard Filter Results:")
        print(f"  Passed: {passed}/{total} ({100*passed/total:.1f}%)")
        print(f"\nExclusion Reasons:")
        for reason, count in failures:
            if count > 0:
                print(f"  - {reason}: {count}")
        print()
        
        self.hard_filter_results = dict(failures)
    
    def score_value_creation_levers(self):
        """Score potential for each value creation lever (1-10)."""
        print("Scoring value creation levers...")
        
        # 1. PROFESSIONALIZATION (Founder dependency, age, systems)
        def score_professionalization(row):
            if row['Ownership_Type'] != "Family/Founder":
                return 2  # Low potential if already professional
            if pd.notna(row['Company_Age_Years']) and row['Company_Age_Years'] > 20:
                return 8  # Mature founder = high professionalization potential
            return 6
        
        self.derived_df['LEVER_Professionalization'] = self.derived_df.apply(score_professionalization, axis=1)
        
        # 2. REVENUE GROWTH (Low CAGR, B2B opportunity, geographic expansion)
        def score_revenue_growth(row):
            score = 5
            if pd.notna(row['Revenue_CAGR_3Y_%']) and row['Revenue_CAGR_3Y_%'] < 0.05:
                score += 3  # Stagnant growth = opportunity
            if row['Market_Type'] == "B2B":
                score += 1  # B2B typically more scalable
            return min(10, score)
        
        self.derived_df['LEVER_Revenue_Growth'] = self.derived_df.apply(score_revenue_growth, axis=1)
        
        # 3. MARGIN EXPANSION (Low margin, high OpEx, supplier opportunities)
        def score_margin_expansion(row):
            if pd.isna(row['EBITDA_Margin_%']):
                return 5
            margin = row['EBITDA_Margin_%']
            if margin < 0.10:
                return 9  # Low margin = high expansion potential
            elif margin < 0.15:
                return 7
            else:
                return 4
        
        self.derived_df['LEVER_Margin_Expansion'] = self.derived_df.apply(score_margin_expansion, axis=1)
        
        # 4. BUY-AND-BUILD (Fragmented market, SME heavy, sector consolidation)
        def score_buy_and_build(row):
            score = 5
            if row['Market_Type'] == "B2B":
                score += 2  # B2B typically more fragmented
            if pd.notna(row['Employee_Count']) and row['Employee_Count'] < 100:
                score += 1  # SME size = consolidation target
            return min(10, score)
        
        self.derived_df['LEVER_Buy_and_Build'] = self.derived_df.apply(score_buy_and_build, axis=1)
        
        # 5. PRICING POWER (Cost-plus, high margin product, low switching cost)
        def score_pricing_power(row):
            score = 5
            if pd.notna(row['EBITDA_Margin_%']) and row['EBITDA_Margin_%'] > 0.20:
                score += 2  # High margin suggests pricing power
            if row['Market_Type'] == "B2B":
                score += 1  # B2B typically has more pricing flexibility
            return min(10, score)
        
        self.derived_df['LEVER_Pricing_Power'] = self.derived_df.apply(score_pricing_power, axis=1)
        
        # 6. CUSTOMER CONCENTRATION (Diversify customer base, sticky contracts)
        def score_customer_concentration(row):
            # Note: Direct customer data not in SABI, use as generic opportunity score
            return 6
        
        self.derived_df['LEVER_Customer_Concentration'] = 6
        
        # 7. DIGITAL TRANSFORMATION (Legacy operations, manual processes, no tech)
        def score_digital_transformation(row):
            # Infer from company age and business model
            score = 5
            if pd.notna(row['Company_Age_Years']) and row['Company_Age_Years'] > 15:
                score += 2  # Older company likely has legacy systems
            if row['Market_Type'] == "B2C/OTHER":
                score += 1  # Consumer-facing businesses often benefit from digitalization
            return min(10, score)
        
        self.derived_df['LEVER_Digital_Transformation'] = self.derived_df.apply(score_digital_transformation, axis=1)
        
        # Calculate average lever score
        lever_cols = [col for col in self.derived_df.columns if col.startswith('LEVER_')]
        self.derived_df['VALUE_CREATION_SCORE'] = self.derived_df[lever_cols].mean(axis=1)
        
        print(f"✓ Value creation levers scored\n")
    
    def score_quality(self):
        """Calculate QUALITY_SCORE (1-10) based on profitability and stability."""
        scores = []
        details = []
        
        for idx, row in self.derived_df.iterrows():
            criteria_scores = []
            criteria_text = []
            
            # EBITDA Margin scoring
            if pd.notna(row['EBITDA_Margin_%']):
                margin = row['EBITDA_Margin_%']
                if margin > 0.25:
                    m_score = 10
                elif margin > 0.18:
                    m_score = 9
                elif margin > 0.10:
                    m_score = 7
                elif margin > 0:
                    m_score = 5
                else:
                    m_score = 2
                criteria_scores.append(m_score)
                criteria_text.append(f"Margin: {margin:.1%}")
            
            # FCF Conversion
            if pd.notna(row['FCF_to_EBITDA_Conversion_%']):
                fcf = row['FCF_to_EBITDA_Conversion_%']
                if fcf > 0.75:
                    f_score = 10
                elif fcf > 0.60:
                    f_score = 8
                elif fcf > 0:
                    f_score = 5
                else:
                    f_score = 2
                criteria_scores.append(f_score)
                criteria_text.append(f"FCF Conv: {fcf:.0%}")
            
            # Debt to EBITDA scoring
            if pd.notna(row['Debt_to_EBITDA']):
                debt = row['Debt_to_EBITDA']
                if debt < 1:
                    d_score = 10
                elif debt < 2:
                    d_score = 9
                elif debt < 3:
                    d_score = 7
                elif debt < 4:
                    d_score = 5
                else:
                    d_score = 2
                criteria_scores.append(d_score)
                criteria_text.append(f"Debt: {debt:.1f}x")
            
            # EBITDA per Employee
            if pd.notna(row['EBITDA_per_Employee']):
                epe = row['EBITDA_per_Employee']
                if epe > 100:
                    e_score = 10
                elif epe > 50:
                    e_score = 8
                elif epe > 20:
                    e_score = 6
                elif epe > 0:
                    e_score = 4
                else:
                    e_score = 1
                criteria_scores.append(e_score)
                criteria_text.append(f"EBITDA/Emp: {epe:.0f}")
            
            # Years Positive EBITDA
            if pd.notna(row['Years_Positive_EBITDA']):
                years = row['Years_Positive_EBITDA']
                if years == 3:
                    y_score = 10
                elif years == 2:
                    y_score = 7
                elif years == 1:
                    y_score = 4
                else:
                    y_score = 1
                criteria_scores.append(y_score)
                criteria_text.append(f"EBITDA+: {int(years)}y")
            
            # Calculate final score
            if criteria_scores:
                final_score = round(np.mean(criteria_scores))
                final_score = max(1, min(10, final_score))
            else:
                final_score = np.nan
            
            scores.append(final_score)
            details.append(" | ".join(criteria_text) if criteria_text else "N/A")
        
        self.derived_df['QUALITY_SCORE'] = scores
        self.derived_df['QUALITY_Details'] = details
    
    def score_growth(self):
        """Calculate GROWTH_SCORE (1-10) based on revenue and EBITDA growth."""
        scores = []
        details = []
        
        for idx, row in self.derived_df.iterrows():
            criteria_scores = []
            criteria_text = []
            
            # Revenue CAGR
            if pd.notna(row['Revenue_CAGR_3Y_%']):
                cagr = row['Revenue_CAGR_3Y_%']
                if cagr > 0.20:
                    r_score = 10
                elif cagr > 0.15:
                    r_score = 9
                elif cagr > 0.08:
                    r_score = 7
                elif cagr > 0:
                    r_score = 5
                else:
                    r_score = 2
                criteria_scores.append(r_score)
                criteria_text.append(f"Rev CAGR: {cagr:.1%}")
            
            # EBITDA CAGR
            if pd.notna(row['EBITDA_CAGR_3Y_%']):
                ebitda_cagr = row['EBITDA_CAGR_3Y_%']
                if ebitda_cagr > 0.25:
                    e_score = 10
                elif ebitda_cagr > 0.15:
                    e_score = 9
                elif ebitda_cagr > 0.05:
                    e_score = 7
                elif ebitda_cagr > -0.05:
                    e_score = 5
                else:
                    e_score = 2
                criteria_scores.append(e_score)
                criteria_text.append(f"EBITDA CAGR: {ebitda_cagr:.1%}")
            
            # Calculate final score
            if criteria_scores:
                final_score = round(np.mean(criteria_scores))
                final_score = max(1, min(10, final_score))
            else:
                final_score = np.nan
            
            scores.append(final_score)
            details.append(" | ".join(criteria_text) if criteria_text else "N/A")
        
        self.derived_df['GROWTH_SCORE'] = scores
        self.derived_df['GROWTH_Details'] = details
    
    def score_sellability(self):
        """Calculate SELLABILITY_SCORE (1-10) based on maturity and structure."""
        scores = []
        details = []
        
        for idx, row in self.derived_df.iterrows():
            criteria_scores = []
            criteria_text = []
            
            # Company Age
            if pd.notna(row['Company_Age_Years']):
                age = row['Company_Age_Years']
                if age > 20:
                    a_score = 10
                elif age > 10:
                    a_score = 9
                elif age > 5:
                    a_score = 7
                elif age > 2:
                    a_score = 5
                else:
                    a_score = 2
                criteria_scores.append(a_score)
                criteria_text.append(f"Age: {int(age)}y")
            
            # Structure Simplicity
            structure = row.get('Structure_Complexity', "Simple")
            if structure == "Simple":
                s_score = 10
            elif structure == "Medium":
                s_score = 7
            else:
                s_score = 5
            criteria_scores.append(s_score)
            criteria_text.append(f"Structure: {structure}")
            
            # Shareholder Concentration
            concentration = row['Shareholder_Concentration']
            if concentration == "HIGH":
                sh_score = 10
            elif concentration == "MEDIUM":
                sh_score = 7
            else:
                sh_score = 5
            criteria_scores.append(sh_score)
            criteria_text.append(f"Concentration: {concentration}")
            
            # Ownership Type (Family/Founder preferred)
            if row['Ownership_Type'] == "Family/Founder":
                o_score = 9
            else:
                o_score = 5
            criteria_scores.append(o_score)
            criteria_text.append(f"Owner: {row['Ownership_Type']}")
            
            # Calculate final score
            if criteria_scores:
                final_score = round(np.mean(criteria_scores))
                final_score = max(1, min(10, final_score))
            else:
                final_score = np.nan
            
            scores.append(final_score)
            details.append(" | ".join(criteria_text) if criteria_text else "N/A")
        
        self.derived_df['SELLABILITY_SCORE'] = scores
        self.derived_df['SELLABILITY_Details'] = details
    
    def calculate_scores(self):
        """Calculate all three scores."""
        print("Calculating acquisition scores...")
        
        self.score_quality()
        self.score_growth()
        self.score_sellability()
        
        print(f"✓ Quality, Growth, and Sellability scores calculated\n")
    
    def calculate_total_score_and_priority(self):
        """Calculate total score and assign priority."""
        print("Calculating total score and priority...")
        
        # Add structure complexity field FIRST
        def classify_structure(row):
            if pd.isna(row.get('Group_Company_Count', None)):
                return "Simple"
            elif row['Group_Company_Count'] <= 5:
                return "Medium"
            else:
                return "Complex"
        
        self.derived_df['Structure_Complexity'] = self.derived_df.apply(classify_structure, axis=1)
        
        # Calculate total score (only for hard filter pass)
        self.derived_df['TOTAL_SCORE'] = np.where(
            self.derived_df['HARD_FILTER_PASS'],
            (self.derived_df['QUALITY_SCORE'] + 
             self.derived_df['GROWTH_SCORE'] + 
             self.derived_df['SELLABILITY_SCORE']),
            np.nan
        )
        
        # Assign priority
        def assign_priority(row):
            if not row['HARD_FILTER_PASS']:
                return "EXCLUDED"
            score = row['TOTAL_SCORE']
            if pd.isna(score):
                return "UNRATED"
            elif score >= 24:
                return "VERY HIGH"
            elif score >= 20:
                return "HIGH"
            elif score >= 16:
                return "MEDIUM"
            elif score >= 12:
                return "LOW"
            else:
                return "EXCLUDE"
        
        self.derived_df['PRIORITY'] = self.derived_df.apply(assign_priority, axis=1)
        
        # Assign category
        def assign_category(row):
            priority = row['PRIORITY']
            
            if priority == "EXCLUDED":
                return "HARD_FILTER_FAIL"
            elif priority == "VERY HIGH":
                if row['Ownership_Type'] == "Family/Founder" and row['FLAG_Hidden_Group'] == "No":
                    return "LOW-HANGING FRUIT"
                else:
                    return "HIDDEN GEM"
            elif priority in ["HIGH"]:
                if row['FLAG_Hidden_Group'] == "Yes" or row['Structure_Complexity'] != "Simple":
                    return "HIDDEN GEM"
                else:
                    return "MEDIUM PROSPECT"
            elif priority == "MEDIUM":
                return "MEDIUM PROSPECT"
            else:
                return "EXCLUDE"
        
        self.derived_df['CATEGORY'] = self.derived_df.apply(assign_category, axis=1)
        
        print(f"✓ Total scores and priority assigned\n")
    
    def run_full_pipeline(self):
        """Execute complete data processing pipeline."""
        print("=" * 100)
        print("ACQUISITION SOURCING - DATA PROCESSING PIPELINE v2.0")
        print("With Hard Filters | Value Creation Levers | Ownership Analysis | Business Model Detection")
        print("=" * 100)
        print()
        
        self.load_raw_data()
        self.calculate_derived_metrics()
        self.detect_business_model()
        self.detect_ownership_structure()
        self.apply_hard_filters()
        self.score_value_creation_levers()
        self.calculate_scores()
        self.calculate_total_score_and_priority()
        
        self.output_df = self.derived_df.copy()
        
        return self.output_df
    
    def export_to_excel(self, output_file="Acquisition_Pipeline_v2.xlsx"):
        """Export results to Excel with multiple analytical sheets."""
        print("Exporting results to Excel...")
        
        priority_order = {
            "VERY HIGH": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, 
            "EXCLUDE": 4, "EXCLUDED": 5, "UNRATED": 6
        }
        
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        
        try:
            # SHEET 0: QUALIFIED LEADS (NEW - Executive Summary for Calling)
            passing = self.output_df[self.output_df['HARD_FILTER_PASS'] == True].copy()
            passing['_priority_order'] = passing['PRIORITY'].map(priority_order).fillna(99)
            passing = passing.sort_values(
                by=['_priority_order', 'TOTAL_SCORE', 'VALUE_CREATION_SCORE'],
                ascending=[True, False, False]
            ).drop(columns=['_priority_order'])
            
            qualified_cols = [
                'Company_Name',
                'PRIORITY',
                'CATEGORY',
                'TOTAL_SCORE',
                'VALUE_CREATION_SCORE',
                'City',
                'Phone',
                'Website',
                'EBITDA_Current',
                'Revenue_Current',
                'Employee_Count',
                'EBITDA_Margin_%',
                'Revenue_CAGR_3Y_%',
                'Company_Age_Years',
                'Ownership_Type',
                'Business_Model',
                'FLAG_Hidden_Group',
                'GROUP_SIGNAL_SCORE'
            ]
            qualified_leads = passing[[col for col in qualified_cols if col in passing.columns]].copy()
            
            # Format for readability
            if 'EBITDA_Current' in qualified_leads.columns:
                qualified_leads['EBITDA_EUR_M'] = qualified_leads['EBITDA_Current'] / 1000
                qualified_leads = qualified_leads.drop(columns=['EBITDA_Current'])
            
            if 'Revenue_Current' in qualified_leads.columns:
                qualified_leads['Revenue_EUR_M'] = qualified_leads['Revenue_Current'] / 1000
                qualified_leads = qualified_leads.drop(columns=['Revenue_Current'])
            
            if 'EBITDA_Margin_%' in qualified_leads.columns:
                qualified_leads['EBITDA_Margin'] = qualified_leads['EBITDA_Margin_%'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
                qualified_leads = qualified_leads.drop(columns=['EBITDA_Margin_%'])
            
            if 'Revenue_CAGR_3Y_%' in qualified_leads.columns:
                qualified_leads['Revenue_Growth_3Y'] = qualified_leads['Revenue_CAGR_3Y_%'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
                qualified_leads = qualified_leads.drop(columns=['Revenue_CAGR_3Y_%'])
            
            if 'Company_Age_Years' in qualified_leads.columns:
                qualified_leads['Age_Years'] = qualified_leads['Company_Age_Years'].apply(lambda x: f"{int(x)}y" if pd.notna(x) else "N/A")
                qualified_leads = qualified_leads.drop(columns=['Company_Age_Years'])
            
            qualified_leads.to_excel(writer, sheet_name="QUALIFIED_LEADS", index=False)
            
            # Sheet 1: Final Output (sorted by priority)
            output_sorted = self.output_df.copy()
            output_sorted['_priority_order'] = output_sorted['PRIORITY'].map(priority_order).fillna(99)
            output_sorted = output_sorted.sort_values(
                by=['_priority_order', 'TOTAL_SCORE'], 
                ascending=[True, False]
            ).drop(columns=['_priority_order'])
            
            output_sorted.to_excel(writer, sheet_name="FINAL_RANKING", index=False)
            
            # Sheet 2: Score Summary
            score_cols = ['Company_Name', 'QUALITY_SCORE', 'GROWTH_SCORE', 'SELLABILITY_SCORE',
                         'TOTAL_SCORE', 'VALUE_CREATION_SCORE', 'PRIORITY', 'CATEGORY']
            score_summary = self.output_df[score_cols].copy()
            score_summary['_priority_order'] = score_summary['PRIORITY'].map(priority_order).fillna(99)
            score_summary = score_summary.sort_values(
                by=['_priority_order', 'TOTAL_SCORE'], 
                ascending=[True, False]
            ).drop(columns=['_priority_order'])
            score_summary.to_excel(writer, sheet_name="SCORE_SUMMARY", index=False)
            
            # Sheet 3: Value Creation Lever Analysis
            lever_cols = ['Company_Name', 'PRIORITY', 'CATEGORY', 'VALUE_CREATION_SCORE',
                         'LEVER_Professionalization', 'LEVER_Revenue_Growth', 'LEVER_Margin_Expansion',
                         'LEVER_Buy_and_Build', 'LEVER_Pricing_Power', 'LEVER_Customer_Concentration',
                         'LEVER_Digital_Transformation']
            lever_analysis = self.output_df[[col for col in lever_cols if col in self.output_df.columns]].copy()
            lever_analysis.to_excel(writer, sheet_name="VALUE_CREATION_LEVERS", index=False)
            
            # Sheet 4: Ownership & Business Model Analysis
            ownership_cols = ['Company_Name', 'PRIORITY', 'Ownership_Type', 'Shareholder_Concentration',
                             'FLAG_Hidden_Group', 'Company_Age_Years', 'Business_Model', 'Market_Type',
                             'Legal_Form']
            ownership_analysis = self.output_df[[col for col in ownership_cols if col in self.output_df.columns]].copy()
            ownership_analysis.to_excel(writer, sheet_name="OWNERSHIP_BUSINESS_MODEL", index=False)
            
            # Sheet 5: Hard Filters Status
            hf_cols = ['Company_Name', 'HARD_FILTER_PASS', 'HARD_FILTER_FAILURES',
                      'EBITDA_Current', 'Debt_to_EBITDA', 'Business_Model',
                      'Ownership_Type', 'Years_Positive_EBITDA']
            hard_filter_df = self.output_df[[col for col in hf_cols if col in self.output_df.columns]].copy()
            hard_filter_df.to_excel(writer, sheet_name="HARD_FILTERS", index=False)
            
            # Sheet 6: Financial Metrics
            fin_cols = ['Company_Name', 'Employee_Count', 'Revenue_Current', 'EBITDA_Current',
                       'EBITDA_Margin_%', 'Cashflow_Margin_%', 'FCF_to_EBITDA_Conversion_%',
                       'EBITDA_per_Employee', 'Revenue_CAGR_3Y_%', 'EBITDA_CAGR_3Y_%', 
                       'Debt_to_EBITDA', 'LT_Debt_Current']
            financial = self.output_df[[col for col in fin_cols if col in self.output_df.columns]].copy()
            financial.to_excel(writer, sheet_name="FINANCIAL_METRICS", index=False)
            
            # Sheet 7: Company Details
            det_cols = ['Company_Name', 'Tax_ID', 'City', 'Province', 'Legal_Form',
                       'Website', 'Phone', 'Founding_Date', 'Company_Age_Years',
                       'Structure_Complexity', 'Employee_Count', 'CNAE_Description']
            details = self.output_df[[col for col in det_cols if col in self.output_df.columns]].copy()
            details.to_excel(writer, sheet_name="COMPANY_DETAILS", index=False)
            
            # Sheet 8: Hidden Group & Multi-Entity Detection
            hg_cols = ['Company_Name', 'PRIORITY', 'FLAG_Hidden_Group', 'GROUP_SIGNAL_SCORE',
                       'FLAG_SHARED_SHAREHOLDER', 'FLAG_SHARED_PHONE', 'FLAG_SHARED_WEBSITE', 
                       'FLAG_SHARED_ADDRESS', 'GUO_Name', 'ISH_Name', 'Ownership_Type']
            hidden_group_df = self.output_df[[col for col in hg_cols if col in self.output_df.columns]].copy()
            hidden_group_df.to_excel(writer, sheet_name="HIDDEN_GROUP_ANALYSIS", index=False)
            
            # Sheet 9: Priority Action List (for sourcing team)
            action_list = passing[[
                'Company_Name', 'PRIORITY', 'CATEGORY', 'Phone', 'Website', 'City'
            ]].copy()
            action_list['CALL_STATUS'] = ""  # Add column for team to track calls
            action_list['NOTES'] = ""  # Add column for call notes
            action_list = action_list.reset_index(drop=True)
            action_list.index = action_list.index + 1  # Start numbering from 1
            action_list.to_excel(writer, sheet_name="ACTION_LIST")
            
            writer.close()
            print(f"✓ Exported to {output_file}\n")
            return output_file
        
        except Exception as e:
            print(f"Error during export: {e}")
            raise
    
    def print_summary(self):
        """Print executive summary focused on qualified leads."""
        print("=" * 100)
        print("EXECUTIVE SUMMARY - QUALIFIED ACQUISITION LEADS")
        print("=" * 100)
        print()
        
        # Hard filter summary
        total = len(self.output_df)
        passed = self.output_df['HARD_FILTER_PASS'].sum()
        failed = total - passed
        
        print("PIPELINE STAGE:")
        print(f"  Total Companies Analyzed: {total:,}")
        print(f"  Passed Hard Filters (QUALIFIED): {passed:,} ({100*passed/total:.1f}%)")
        print(f"  Failed Hard Filters (EXCLUDED): {failed:,} ({100*failed/total:.1f}%)")
        print()
        
        # Qualified leads by priority
        passing = self.output_df[self.output_df['HARD_FILTER_PASS'] == True]
        priority_counts = passing['PRIORITY'].value_counts()
        
        print("QUALIFIED LEADS BY PRIORITY:")
        print()
        for priority in ["VERY HIGH", "HIGH", "MEDIUM"]:
            count = priority_counts.get(priority, 0)
            pct = 100 * count / len(passing) if len(passing) > 0 else 0
            if count > 0:
                print(f"  {priority:12s}: {count:4d} companies ({pct:5.1f}%) - READY TO CALL")
        print()
        
        # Category breakdown (qualified only)
        category_counts = passing['CATEGORY'].value_counts()
        print("LEAD QUALITY CATEGORIES (Qualified):")
        print()
        for category in ["LOW-HANGING FRUIT", "HIDDEN GEM", "MEDIUM PROSPECT"]:
            count = category_counts.get(category, 0)
            pct = 100 * count / len(passing) if len(passing) > 0 else 0
            if count > 0:
                if category == "LOW-HANGING FRUIT":
                    desc = "Clean, simple structure, family-owned"
                elif category == "HIDDEN GEM":
                    desc = "High potential but complex structure or hidden groups"
                else:
                    desc = "Medium opportunity, selective targeting"
                print(f"  {category:20s}: {count:4d} ({pct:5.1f}%) - {desc}")
        print()
        
        # Business model focus (qualified only)
        print("QUALIFIED LEADS BY BUSINESS MODEL:")
        bm_counts = passing['Business_Model'].value_counts()
        for bm in ["RECURRING", "MIXED", "UNCLEAR"]:
            count = bm_counts.get(bm, 0)
            pct = 100 * count / len(passing) if len(passing) > 0 else 0
            if count > 0:
                print(f"  {bm:15s}: {count:4d} ({pct:5.1f}%)")
        print()
        
        # Ownership focus (qualified only)
        print("QUALIFIED LEADS BY OWNERSHIP:")
        own_counts = passing['Ownership_Type'].value_counts()
        for own in ["Family/Founder", "VC/PE/CORP"]:
            count = own_counts.get(own, 0)
            pct = 100 * count / len(passing) if len(passing) > 0 else 0
            if count > 0:
                print(f"  {own:18s}: {count:4d} ({pct:5.1f}%)")
        print()
        
        # Top 15 calling targets
        print("TOP 15 CALLING TARGETS (Qualified Leads):")
        print()
        top_15 = passing.nlargest(15, 'TOTAL_SCORE')[[
            'Company_Name', 'PRIORITY', 'CATEGORY', 'TOTAL_SCORE', 
            'VALUE_CREATION_SCORE', 'Phone', 'City'
        ]]
        
        print(f"{'Rank':<4} {'Company Name':<35} {'Priority':<10} {'Score':<6} {'Value':<6} {'City':<15}")
        print("-" * 100)
        
        for i, (idx, row) in enumerate(top_15.iterrows(), 1):
            company = row['Company_Name'][:32]
            priority = row['PRIORITY']
            score = row['TOTAL_SCORE']
            value = row['VALUE_CREATION_SCORE']
            city = row['City'][:12] if pd.notna(row['City']) else "N/A"
            print(f"{i:<4} {company:<35} {priority:<10} {score:<6.0f} {value:<6.1f} {city:<15}")
        print()
        
        # Score statistics
        print("SCORE STATISTICS (Qualified Leads Only):")
        print(f"  Mean Total Score: {passing['TOTAL_SCORE'].mean():.1f}/30")
        print(f"  Median Total Score: {passing['TOTAL_SCORE'].median():.1f}/30")
        print(f"  Mean Value Creation Score: {passing['VALUE_CREATION_SCORE'].mean():.1f}/10")
        print()
        
        # Multi-entity risk (qualified)
        hidden_groups = (passing['FLAG_Hidden_Group'] == 'Yes').sum()
        print(f"MULTI-ENTITY COMPLEXITY (Qualified Leads):")
        print(f"  Hidden Groups Detected: {hidden_groups} ({100*hidden_groups/len(passing) if len(passing) > 0 else 0:.1f}%)")
        print(f"  Simple Structures (Low Risk): {len(passing) - hidden_groups} ({100*(len(passing)-hidden_groups)/len(passing) if len(passing) > 0 else 0:.1f}%)")
        print()


def main():
    """Main entry point."""
    processor = AcquisitionDataProcessor()
    
    try:
        processor.run_full_pipeline()
        
        if len(processor.output_df) > 0:
            processor.export_to_excel()
            processor.print_summary()
            
            csv_file = "Acquisition_Pipeline_v2.csv"
            processor.output_df.to_csv(csv_file, index=False)
            print(f"[+] Also saved to {csv_file}\n")
        else:
            print("WARNING: No data found in sheet.")
        
        return processor, processor.output_df
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    processor, output_df = main()

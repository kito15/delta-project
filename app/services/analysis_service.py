import os
import pandas as pd
import numpy as np
from datetime import datetime
import re

class AnalysisService:
    """Service for analyzing CSV data quality"""

    @staticmethod
    def analyze_csv(file_path):
        """Main analysis function - analyzes CSV file and returns comprehensive results"""
        df = pd.read_csv(file_path)

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        analysis = {
            'filename': filename,
            'fileSize': AnalysisService.format_file_size(file_size),
            'timestamp': datetime.utcnow().isoformat(),
            'totalRows': len(df),
            'totalColumns': len(df.columns),
            'columns': [],
            'issues': [],
            'qualityScore': 0
        }

        for column in df.columns:
            column_analysis = AnalysisService.analyze_column(df, column)
            analysis['columns'].append(column_analysis)

        AnalysisService.detect_missing_values(analysis, df)
        AnalysisService.detect_invalid_formats(analysis, df)
        AnalysisService.detect_outliers(analysis, df)
        AnalysisService.detect_logical_issues(analysis, df)
        AnalysisService.detect_duplicates(analysis, df)

        analysis['qualityScore'] = AnalysisService.calculate_quality_score(analysis)

        return analysis

    @staticmethod
    def analyze_column(df, column_name):
        """Analyze individual column"""
        series = df[column_name]

        non_empty = series.dropna()
        total = len(series)
        missing_count = total - len(non_empty)
        missing_percentage = round((missing_count / total * 100), 1) if total > 0 else 0

        unique_count = series.nunique()
        unique_percentage = round((unique_count / len(non_empty) * 100), 1) if len(non_empty) > 0 else 0

        data_type = AnalysisService.infer_data_type(non_empty)

        return {
            'name': column_name,
            'type': data_type,
            'totalValues': total,
            'nonEmptyValues': len(non_empty),
            'missingCount': missing_count,
            'missingPercentage': str(missing_percentage),
            'uniqueCount': unique_count,
            'uniquePercentage': str(unique_percentage)
        }

    @staticmethod
    def infer_data_type(series):
        """Infer the data type of a column"""
        if len(series) == 0:
            return 'unknown'

        sample = series.head(100)

        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        email_count = sum(1 for val in sample.astype(str) if email_pattern.match(str(val)))

        if email_count > len(sample) * 0.5:
            return 'email'

        try:
            pd.to_datetime(sample, errors='coerce')
            date_count = sample.astype(str).str.contains('-').sum()
            if date_count > len(sample) * 0.5:
                return 'date'
        except:
            pass

        numeric_count = pd.to_numeric(sample, errors='coerce').notna().sum()
        if numeric_count > len(sample) * 0.8:
            return 'numeric'

        return 'text'

    @staticmethod
    def detect_missing_values(analysis, df):
        """Detect missing values in columns"""
        for col_analysis in analysis['columns']:
            if col_analysis['missingCount'] > 0:
                severity = 'error' if float(col_analysis['missingPercentage']) > 10 else 'warning'

                analysis['issues'].append({
                    'type': 'Missing Values',
                    'severity': severity,
                    'count': col_analysis['missingCount'],
                    'percentage': col_analysis['missingPercentage'],
                    'column': col_analysis['name'],
                    'description': f"{col_analysis['missingPercentage']}% of values are missing in column \"{col_analysis['name']}\""
                })

    @staticmethod
    def detect_invalid_formats(analysis, df):
        """Detect invalid formats (email, dates, etc.)"""
        for col_analysis in analysis['columns']:
            column_name = col_analysis['name']
            series = df[column_name].dropna()

            if col_analysis['type'] == 'email':
                email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
                invalid_count = sum(1 for val in series if not email_pattern.match(str(val)))

                if invalid_count > 0:
                    analysis['issues'].append({
                        'type': 'Invalid Format',
                        'severity': 'error',
                        'count': invalid_count,
                        'column': column_name,
                        'description': f"{invalid_count} invalid email formats in column \"{column_name}\""
                    })

            if col_analysis['type'] == 'date':
                try:
                    dates = pd.to_datetime(series, errors='coerce')
                    future_dates = (dates > pd.Timestamp.now()).sum()

                    if future_dates > 0:
                        analysis['issues'].append({
                            'type': 'Invalid Date',
                            'severity': 'warning',
                            'count': int(future_dates),
                            'column': column_name,
                            'description': f"{future_dates} future dates detected in column \"{column_name}\""
                        })
                except:
                    pass

    @staticmethod
    def detect_outliers(analysis, df):
        """Detect statistical outliers in numeric columns"""
        for col_analysis in analysis['columns']:
            if col_analysis['type'] == 'numeric':
                column_name = col_analysis['name']
                series = pd.to_numeric(df[column_name], errors='coerce').dropna()

                if len(series) > 0:
                    mean = series.mean()
                    std = series.std()

                    if std > 0:
                        outliers = ((series - mean).abs() > 3 * std).sum()

                        if outliers > 0:
                            analysis['issues'].append({
                                'type': 'Statistical Outlier',
                                'severity': 'info',
                                'count': int(outliers),
                                'column': column_name,
                                'description': f"{outliers} statistical outliers detected in column \"{column_name}\""
                            })

    @staticmethod
    def detect_logical_issues(analysis, df):
        """Detect logical inconsistencies"""
        positive_keywords = ['age', 'price', 'quantity', 'stock', 'amount', 'cost', 'selling']

        for col_analysis in analysis['columns']:
            if col_analysis['type'] == 'numeric':
                column_name = col_analysis['name']

                if any(keyword in column_name.lower() for keyword in positive_keywords):
                    series = pd.to_numeric(df[column_name], errors='coerce').dropna()
                    negative_count = (series < 0).sum()

                    if negative_count > 0:
                        analysis['issues'].append({
                            'type': 'Logical Inconsistency',
                            'severity': 'error',
                            'count': int(negative_count),
                            'column': column_name,
                            'description': f"{negative_count} negative values in column \"{column_name}\" where positive expected"
                        })

        cost_cols = [col for col in df.columns if 'cost' in col.lower() and 'price' in col.lower()]
        selling_cols = [col for col in df.columns if 'selling' in col.lower() and 'price' in col.lower()]

        if cost_cols and selling_cols:
            cost_col = cost_cols[0]
            selling_col = selling_cols[0]

            cost_series = pd.to_numeric(df[cost_col], errors='coerce')
            selling_series = pd.to_numeric(df[selling_col], errors='coerce')

            price_issues = ((selling_series < cost_series) & cost_series.notna() & selling_series.notna()).sum()

            if price_issues > 0:
                analysis['issues'].append({
                    'type': 'Logical Inconsistency',
                    'severity': 'error',
                    'count': int(price_issues),
                    'description': f"{price_issues} products with selling price below cost price"
                })

        stock_cols = [col for col in df.columns if 'stock' in col.lower() and 'current' in col.lower()]
        reorder_cols = [col for col in df.columns if 'reorder' in col.lower()]

        if stock_cols and reorder_cols:
            stock_col = stock_cols[0]
            reorder_col = reorder_cols[0]

            stock_series = pd.to_numeric(df[stock_col], errors='coerce')
            reorder_series = pd.to_numeric(df[reorder_col], errors='coerce')

            stock_issues = ((stock_series < reorder_series) & stock_series.notna() & reorder_series.notna()).sum()

            if stock_issues > 0:
                analysis['issues'].append({
                    'type': 'Business Rule Violation',
                    'severity': 'warning',
                    'count': int(stock_issues),
                    'description': f"{stock_issues} products with stock level below reorder threshold"
                })

    @staticmethod
    def detect_duplicates(analysis, df):
        """Detect duplicate records"""
        duplicate_count = df.duplicated().sum()

        if duplicate_count > 0:
            analysis['issues'].append({
                'type': 'Duplicate Records',
                'severity': 'warning',
                'count': int(duplicate_count),
                'description': f"{duplicate_count} duplicate records detected in dataset"
            })

    @staticmethod
    def calculate_quality_score(analysis):
        """Calculate overall quality score (0-100)"""
        score = 100

        avg_missing = sum(float(col['missingPercentage']) for col in analysis['columns']) / len(analysis['columns'])
        score -= avg_missing

        error_count = sum(1 for issue in analysis['issues'] if issue['severity'] == 'error')
        warning_count = sum(1 for issue in analysis['issues'] if issue['severity'] == 'warning')

        score -= error_count * 5
        score -= warning_count * 2

        return max(0, min(100, int(score)))

    @staticmethod
    def format_file_size(bytes_size):
        """Format file size in human-readable format"""
        if bytes_size == 0:
            return '0 B'

        sizes = ['B', 'KB', 'MB', 'GB']
        k = 1024
        i = 0
        size = bytes_size

        while size >= k and i < len(sizes) - 1:
            size /= k
            i += 1

        return f"{round(size, 2)} {sizes[i]}"

    @staticmethod
    def get_affected_rows(file_path, issue_type, column_name=None, limit=50, offset=0):
        """
        Get rows affected by a specific issue

        Args:
            file_path: Path to CSV file
            issue_type: Type of issue (Missing Values, Invalid Format, etc.)
            column_name: Column affected by issue (optional)
            limit: Maximum rows to return
            offset: Offset for pagination

        Returns:
            Dictionary with rows, columns, total_count, has_more
        """
        try:
            df = pd.read_csv(file_path)
            total_rows = len(df)

            if issue_type == 'Missing Values' and column_name:
                mask = df[column_name].isna() | (df[column_name].astype(str).str.strip() == '')
                filtered_df = df[mask]

            elif issue_type == 'Invalid Format' and column_name:
                email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
                mask = ~df[column_name].dropna().astype(str).apply(lambda x: bool(email_pattern.match(x)))
                filtered_df = df[df[column_name].notna()][mask]

            elif issue_type == 'Invalid Date' and column_name:
                dates = pd.to_datetime(df[column_name], errors='coerce')
                future_mask = dates > pd.Timestamp.now()
                filtered_df = df[future_mask]

            elif issue_type == 'Statistical Outlier' and column_name:
                # Values > 3 standard deviations from mean
                series = pd.to_numeric(df[column_name], errors='coerce')
                mean = series.mean()
                std = series.std()

                if std > 0:
                    mask = ((series - mean).abs() > 3 * std) & series.notna()
                    filtered_df = df[mask]
                else:
                    filtered_df = pd.DataFrame()

            elif issue_type == 'Logical Inconsistency':
                if column_name:
                    positive_keywords = ['age', 'price', 'quantity', 'stock', 'amount', 'cost', 'selling']
                    if any(keyword in column_name.lower() for keyword in positive_keywords):
                        series = pd.to_numeric(df[column_name], errors='coerce')
                        mask = (series < 0) & series.notna()
                        filtered_df = df[mask]
                    else:
                        filtered_df = pd.DataFrame()
                else:
                    cost_cols = [col for col in df.columns if 'cost' in col.lower() and 'price' in col.lower()]
                    selling_cols = [col for col in df.columns if 'selling' in col.lower() and 'price' in col.lower()]

                    if cost_cols and selling_cols:
                        cost_col = cost_cols[0]
                        selling_col = selling_cols[0]
                        cost_series = pd.to_numeric(df[cost_col], errors='coerce')
                        selling_series = pd.to_numeric(df[selling_col], errors='coerce')
                        mask = (selling_series < cost_series) & cost_series.notna() & selling_series.notna()
                        filtered_df = df[mask]
                    else:
                        filtered_df = pd.DataFrame()

            elif issue_type == 'Business Rule Violation':
                stock_cols = [col for col in df.columns if 'stock' in col.lower() and 'current' in col.lower()]
                reorder_cols = [col for col in df.columns if 'reorder' in col.lower()]

                if stock_cols and reorder_cols:
                    stock_col = stock_cols[0]
                    reorder_col = reorder_cols[0]
                    stock_series = pd.to_numeric(df[stock_col], errors='coerce')
                    reorder_series = pd.to_numeric(df[reorder_col], errors='coerce')
                    mask = (stock_series < reorder_series) & stock_series.notna() & reorder_series.notna()
                    filtered_df = df[mask]
                else:
                    filtered_df = pd.DataFrame()

            elif issue_type == 'Duplicate Records':
                mask = df.duplicated(keep=False)
                filtered_df = df[mask]

            else:
                filtered_df = pd.DataFrame()

            total_affected = len(filtered_df)

            paginated_df = filtered_df.iloc[offset:offset + limit]

            rows = []
            for idx, row in paginated_df.iterrows():
                row_dict = {'row_index': int(idx) + 1}
                row_dict.update({k: None if pd.isna(v) else v for k, v in row.to_dict().items()})
                rows.append(row_dict)

            columns = ['row_index'] + list(df.columns)

            return {
                'rows': rows,
                'columns': columns,
                'total_count': total_affected,
                'has_more': (offset + limit) < total_affected,
                'affected_column': column_name
            }

        except Exception as e:
            return {
                'rows': [],
                'columns': [],
                'total_count': 0,
                'has_more': False,
                'error': str(e)
            }


# services/report_service.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Report Service for PetBag Boarding System

from datetime import datetime, timedelta
from models.pet import Pet
from services.boarding_service import BoardingService

class ReportService:
    
    #generate detailed occupancy report for the specified period
    @staticmethod
    def get_occupancy_report(db, period_days=30):
        
        cursor = db.connection.cursor(dictionary=True)
        
        # calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # get occupancy data
        cursor.execute("""
            SELECT 
                DATE(b.check_in) as date,
                COUNT(*) as total_boardings,
                SUM(CASE WHEN p.pet_type = 'dog' THEN 1 ELSE 0 END) as dog_count,
                SUM(CASE WHEN p.pet_type = 'cat' THEN 1 ELSE 0 END) as cat_count,
                AVG(b.days_stay) as avg_stay_duration
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            WHERE b.check_in BETWEEN %s AND %s
            GROUP BY DATE(b.check_in)
            ORDER BY DATE(b.check_in) DESC
        """, (start_date, end_date))
        daily_data = cursor.fetchall()
        
        # get current occupancy
        cursor.execute("""
            SELECT 
                p.pet_type,
                COUNT(*) as count
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            WHERE b.check_out IS NULL
            GROUP BY p.pet_type
        """)
        current_occupancy = cursor.fetchall()
        
        # get capacity 
        cursor.execute("""
            SELECT 
                COUNT(*) as total_current,
                AVG(b.days_stay) as avg_days_stay
            FROM Boarding b
            WHERE b.check_out IS NULL
        """)
        current_stats = cursor.fetchone()
        
        cursor.close()
        
        # format the report
        report = "OCCUPANCY REPORT\n"
        report += "=" * 60 + "\n"
        report += f"Report Period: {start_date} to {end_date} ({period_days} days)\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        report += "CURRENT OCCUPANCY STATUS\n"
        report += "-" * 40 + "\n"
        
        dog_count = 0
        cat_count = 0
        for occ in current_occupancy:
            if occ['pet_type'].lower() == 'dog':
                dog_count = occ['count']
            else:
                cat_count = occ['count']
        
        total_capacity = 42  # 30 dogs + 12 cats
        current_total = dog_count + cat_count
        occupancy_rate = (current_total / total_capacity) * 100 if total_capacity > 0 else 0
        
        report += f"Dogs: {dog_count}/30 spaces ({dog_count/30*100:.1f}% occupied)\n"
        report += f"Cats: {cat_count}/12 spaces ({cat_count/12*100:.1f}% occupied)\n"
        report += f"Total: {current_total}/42 spaces ({occupancy_rate:.1f}% occupied)\n"
        report += f"Average Stay Duration: {current_stats['avg_days_stay'] or 0:.1f} days\n\n"
        
        # daily section
        report += "DAILY OCCUPANCY BREAKDOWN\n"
        report += "-" * 60 + "\n"
        report += f"{'Date':<12} {'Total':<8} {'Dogs':<8} {'Cats':<8} {'Avg Stay':<10}\n"
        report += "-" * 60 + "\n"
        
        total_boardings = 0
        total_dogs = 0
        total_cats = 0
        
        for day in daily_data:
            date_str = str(day['date']) if day['date'] else "No Date"
            
            report += f"{date_str:<12} {day['total_boardings']:<8} "
            report += f"{day['dog_count']:<8} {day['cat_count']:<8} "
            report += f"{day['avg_stay_duration'] or 0:<10.1f}\n"
            
            total_boardings += day['total_boardings']
            total_dogs += day['dog_count']
            total_cats += day['cat_count']
        
        report += "-" * 60 + "\n"
        
        # summary section
        report += "\nSUMMARY STATISTICS\n"
        report += "-" * 40 + "\n"
        
        if len(daily_data) > 0:
            avg_daily_boardings = total_boardings / len(daily_data)
            dog_percentage = (total_dogs / total_boardings * 100) if total_boardings > 0 else 0
            cat_percentage = (total_cats / total_boardings * 100) if total_boardings > 0 else 0
            
            report += f"Total Boardings: {total_boardings}\n"
            report += f"Average Daily Boardings: {avg_daily_boardings:.1f}\n"
            report += f"Dog Boardings: {total_dogs} ({dog_percentage:.1f}%)\n"
            report += f"Cat Boardings: {total_cats} ({cat_percentage:.1f}%)\n"
        
        # peak days 
        if len(daily_data) > 0:
            peak_day = max(daily_data, key=lambda x: x['total_boardings'])
            peak_date_str = str(peak_day['date']) if peak_day['date'] else "Unknown"
            report += f"\nPeak Day: {peak_date_str} ({peak_day['total_boardings']} boardings)\n"
        
        return report
    
    #generate detailed revenue report for the specified period
    @staticmethod
    def get_revenue_report(db, period_days=30):
        
        cursor = db.connection.cursor(dictionary=True)
        
        # calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # get revenue data
        cursor.execute("""
            SELECT 
                DATE(b.check_in) as date,
                COUNT(*) as total_boardings,
                SUM(b.amount_due) as daily_revenue,
                SUM(CASE WHEN p.pet_type = 'dog' THEN b.amount_due ELSE 0 END) as dog_revenue,
                SUM(CASE WHEN p.pet_type = 'cat' THEN b.amount_due ELSE 0 END) as cat_revenue,
                SUM(CASE WHEN b.grooming_requested = 1 AND p.pet_type = 'dog' THEN 1 ELSE 0 END) as grooming_count,
                SUM(CASE WHEN g.price IS NOT NULL THEN g.price ELSE 0 END) as grooming_revenue
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            LEFT JOIN Grooming g ON b.boarding_id = g.boarding_id
            WHERE b.check_in BETWEEN %s AND %s
            GROUP BY DATE(b.check_in)
            ORDER BY DATE(b.check_in) DESC
        """, (start_date, end_date))
        daily_data = cursor.fetchall()
        
        # get revenue by pet type
        cursor.execute("""
            SELECT 
                p.pet_type,
                COUNT(*) as count,
                SUM(b.amount_due) as revenue,
                AVG(b.amount_due) as avg_revenue
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            WHERE b.check_in BETWEEN %s AND %s
            GROUP BY p.pet_type
        """, (start_date, end_date))
        pet_type_revenue = cursor.fetchall()
        
        # get grooming revenue breakdown
        cursor.execute("""
            SELECT 
                COUNT(*) as total_grooming,
                SUM(g.price) as total_grooming_revenue,
                AVG(g.price) as avg_grooming_price
            FROM Grooming g
            JOIN Boarding b ON g.boarding_id = b.boarding_id
            WHERE b.check_in BETWEEN %s AND %s
        """, (start_date, end_date))
        grooming_stats = cursor.fetchone()
        
        # get upcoming revenue 
        cursor.execute("""
            SELECT 
                SUM(b.amount_due) as upcoming_revenue,
                COUNT(*) as upcoming_count
            FROM Boarding b
            WHERE b.check_out IS NULL
        """)
        upcoming = cursor.fetchone()
        
        cursor.close()
        
        # format the report
        report = "REVENUE REPORT\n"
        report += "=" * 60 + "\n"
        report += f"Report Period: {start_date} to {end_date} ({period_days} days)\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        report += "CURRENT PRICING\n"
        report += "-" * 40 + "\n"
        report += f"Boarding - Dogs: ${BoardingService.BOARDING_PRICES['dog']}/day\n"
        report += f"Boarding - Cats: ${BoardingService.BOARDING_PRICES['cat']}/day\n"
        report += "Grooming - Dogs (by weight):\n"
        for tier, details in BoardingService.GROOMING_PRICES.items():
            max_weight = "and above" if details['max'] == float('inf') else details['max']
            if details['max'] == float('inf'):
                report += f"  {tier.title()} ({details['min']} lbs {max_weight}): ${details['price']}\n"
            else:
                report += f"  {tier.title()} ({details['min']}-{max_weight} lbs): ${details['price']}\n"
        report += "\n"
        
        # summary section
        report += "REVENUE SUMMARY\n"
        report += "-" * 40 + "\n"
        
        total_revenue = 0
        total_boardings = 0
        total_grooming = 0
        grooming_revenue = 0
        
        for day in daily_data:
            total_revenue += day['daily_revenue'] or 0
            total_boardings += day['total_boardings'] or 0
            total_grooming += day['grooming_count'] or 0
            grooming_revenue += day['grooming_revenue'] or 0
        
        boarding_revenue = total_revenue - grooming_revenue
        
        report += f"Total Boardings: {total_boardings}\n"
        report += f"Total Revenue: ${total_revenue:,.2f}\n"
        report += f"  • Boarding Revenue: ${boarding_revenue:,.2f}\n"
        report += f"  • Grooming Revenue: ${grooming_revenue:,.2f}\n"
        report += f"Grooming Services: {total_grooming}\n"
        if grooming_stats and grooming_stats['total_grooming'] > 0:
            report += f"Average Grooming Price: ${grooming_stats['avg_grooming_price'] or 0:,.2f}\n"
        if total_boardings > 0:
            report += f"Average Revenue per Booking: ${total_revenue/total_boardings:,.2f}\n"
        else:
            report += "Average Revenue per Booking: $0.00\n"
        
        #  by pet type
        report += "\nREVENUE BY PET TYPE\n"
        report += "-" * 40 + "\n"
        
        dog_rev = 0
        cat_rev = 0
        dog_count = 0
        cat_count = 0
        
        for pet_type in pet_type_revenue:
            if pet_type['pet_type'].lower() == 'dog':
                dog_rev = pet_type['revenue'] or 0
                dog_count = pet_type['count'] or 0
                dog_avg = pet_type['avg_revenue'] or 0
            else:
                cat_rev = pet_type['revenue'] or 0
                cat_count = pet_type['count'] or 0
                cat_avg = pet_type['avg_revenue'] or 0
        
        report += f"Dogs: {dog_count} boardings, ${dog_rev:,.2f} revenue (avg ${dog_avg:,.2f})\n"
        report += f"Cats: {cat_count} boardings, ${cat_rev:,.2f} revenue (avg ${cat_avg:,.2f})\n"
        
        # daily section
        report += "\nDAILY REVENUE BREAKDOWN\n"
        report += "-" * 80 + "\n"
        report += f"{'Date':<12} {'Boardings':<10} {'Revenue':<12} {'Dogs':<10} {'Cats':<10} {'Grooming':<10}\n"
        report += "-" * 80 + "\n"
        
        for day in daily_data:
            date_str = str(day['date']) if day['date'] else "No Date"
            
            report += f"{date_str:<12} {day['total_boardings']:<10} "
            report += f"${day['daily_revenue'] or 0:<11,.2f} "
            report += f"${day['dog_revenue'] or 0:<10,.2f} "
            report += f"${day['cat_revenue'] or 0:<10,.2f} "
            report += f"{day['grooming_count'] or 0:<10}\n"
        
        report += "-" * 80 + "\n"
        
        report += "\nFINANCIAL METRICS\n"
        report += "-" * 40 + "\n"
        
        if len(daily_data) > 0:
            avg_daily_revenue = total_revenue / len(daily_data)
            report += f"Average Daily Revenue: ${avg_daily_revenue:,.2f}\n"
            report += f"Projected Monthly Revenue: ${avg_daily_revenue * 30:,.2f}\n"
            report += f"Projected Annual Revenue: ${avg_daily_revenue * 365:,.2f}\n"
        
        # upcoming revenue
        if upcoming and upcoming['upcoming_revenue']:
            report += f"\nUPCOMING REVENUE (Current Boardings)\n"
            report += "-" * 40 + "\n"
            report += f"Pending Boardings: {upcoming['upcoming_count'] or 0}\n"
            report += f"Pending Revenue: ${upcoming['upcoming_revenue'] or 0:,.2f}\n"
        
        return report
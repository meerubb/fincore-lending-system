import customtkinter as ctk
import pyodbc
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==================== DATABASE CONNECTION ====================
def get_db_connection():
    try:
        # We bypass the instance name (\Zain) and go straight to the port (1433)
        # This bypasses all the "Error Locating Server" naming issues.
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=127.0.0.1,1433;"  # <--- Use a comma then the port!
            "DATABASE=FinCore;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str)
        print("✅ SUCCESS! Connected via Port!")
        return conn
    except Exception as e:
        print(f"🔴 Connection Error: {e}")
        return None
# =============================================================

# --- GUI Setup ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BankEnterpriseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("FinCore Banking Management System")
        self.geometry("1100x700")

        self.db_conn = get_db_connection()

        # Split into Sidebar and Main Content Area
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== SIDEBAR ====================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1) 

        logo_label = ctk.CTkLabel(self.sidebar, text="FinCore\nBanking", font=ctk.CTkFont(size=24, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        # Sidebar Buttons
        btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="transparent", border_width=1, hover_color="#333333", command=self.show_dashboard)
        btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        btn_customers = ctk.CTkButton(self.sidebar, text="Customers", fg_color="transparent", border_width=1, hover_color="#333333", command=self.show_customers)
        btn_customers.grid(row=2, column=0, padx=20, pady=10)

        btn_loans = ctk.CTkButton(self.sidebar, text="Loan Portfolio", fg_color="transparent", border_width=1, hover_color="#333333", command=self.show_loans)
        btn_loans.grid(row=3, column=0, padx=20, pady=10)

        btn_payments = ctk.CTkButton(self.sidebar, text="Payments", fg_color="transparent", border_width=1, hover_color="#333333", command=self.show_payments)
        btn_payments.grid(row=4, column=0, padx=20, pady=10)

        btn_risk = ctk.CTkButton(self.sidebar, text="Risk & Defaulters", fg_color="transparent", border_width=1, hover_color="#333333", command=self.show_risk_management)
        btn_risk.grid(row=5, column=0, padx=20, pady=10)
        
        btn_audit = ctk.CTkButton(self.sidebar, text="Audit & Security", fg_color="transparent", border_width=1, hover_color="#333333", command=self.show_audit)
        btn_audit.grid(row=6, column=0, padx=20, pady=10)

        # Status indicator at the bottom of sidebar
        status_text = "🟢 Connected" if self.db_conn else "🔴 Disconnected"
        status_color = "#2ecc71" if self.db_conn else "#e74c3c"
        self.status_label = ctk.CTkLabel(self.sidebar, text=status_text, text_color=status_color, font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.grid(row=7, column=0, padx=20, pady=20)

        # ==================== MAIN CONTENT AREA ====================
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Start by showing Dashboard
        self.show_dashboard()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==================== DASHBOARD ====================
    def show_dashboard(self):
        self.clear_main_frame()
        label = ctk.CTkLabel(self.main_frame, text="FinCore | Executive Dashboard", font=ctk.CTkFont(size=28, weight="bold"))
        label.pack(pady=(20, 10), padx=20, anchor="w")

        if not self.db_conn:
            ctk.CTkLabel(self.main_frame, text="🔴 Database Not Connected", text_color="red").pack(pady=20)
            return

        try:
            cursor = self.db_conn.cursor()
            
            # --- 1. TOP METRIC CARDS ---
            cursor.execute("SELECT * FROM vw_Bank_Dashboard_Stats")
            stats = cursor.fetchone()

            if not stats:
                ctk.CTkLabel(self.main_frame, text="No data available in Dashboard View.", text_color="gray").pack(pady=20)
                return

            total_cust = stats.TotalCustomers or 0
            total_lent = stats.TotalMoneyLent or 0
            total_fines = stats.TotalFinesAccumulated or 0
            rescheduled = stats.RescheduledLoans or 0
            secured = stats.SecuredLoans or 0

            grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            grid_frame.pack(fill="x", padx=20, pady=5)
            grid_frame.grid_columnconfigure((0, 1, 2), weight=1) 

            def create_card(parent, title, value, color, row, col):
                card = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=15, height=120)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                card.grid_propagate(False) 
                
                ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color="gray").pack(pady=(20, 5))
                ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color=color).pack()

            create_card(grid_frame, "Total Customers", f"{total_cust}", "#3498db", 0, 0)
            create_card(grid_frame, "Total Money Lent", f"Rs. {total_lent:,.0f}", "#2ecc71", 0, 1)
            create_card(grid_frame, "Fines (Arrears)", f"Rs. {total_fines:,.0f}", "#e74c3c", 0, 2)

            create_card(grid_frame, "Rescheduled Loans", f"{rescheduled}", "#f39c12", 1, 0)
            create_card(grid_frame, "Secured Assets", f"{secured}", "#9b59b6", 1, 1)
            create_card(grid_frame, "System Status", "All Systems Optimal", "#2ecc71", 1, 2)

            # --- 2. ANALYTICS CHARTS AREA ---
            chart_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Use matplotlib with a dark background theme to match your app
            plt.style.use('dark_background')

            # -- Chart 1: Risk Classification Pie Chart --
            cursor.execute("""
                SELECT RiskLevel, COUNT(*) as Count 
                FROM vw_Risk_Classification 
                GROUP BY RiskLevel
            """)
            risk_data = cursor.fetchall()
            
            if risk_data:
                labels = [row.RiskLevel for row in risk_data]
                sizes = [row.Count for row in risk_data]
                
                # Custom colors for risk (Green, Yellow, Red)
                color_map = {'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12', 'High Risk': '#e74c3c'}
                colors = [color_map.get(label, '#95a5a6') for label in labels]

                fig_pie = plt.Figure(figsize=(4, 4), facecolor='#1e1e1e')
                ax_pie = fig_pie.add_subplot(111)
                ax_pie.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, textprops={'color': 'white'})
                ax_pie.set_title("Customer Risk Distribution", color='white', fontweight='bold')

                canvas_pie = FigureCanvasTkAgg(fig_pie, master=chart_frame)
                canvas_pie.draw()
                canvas_pie.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10)

            # -- Chart 2: Loan Status Bar Chart --
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN ReasonForDefault IS NOT NULL AND ReasonForDefault NOT IN ('', ' ', 'NULL', 'None', '0') THEN 'Defaulted'
                        WHEN IsRescheduled = 1 THEN 'Rescheduled'
                        WHEN LoanEndDate < GETDATE() THEN 'Overdue'
                        ELSE 'Active'
                    END AS LoanStatus,
                    COUNT(*) as Count
                FROM LOAN
                GROUP BY 
                    CASE 
                        WHEN ReasonForDefault IS NOT NULL AND ReasonForDefault NOT IN ('', ' ', 'NULL', 'None', '0') THEN 'Defaulted'
                        WHEN IsRescheduled = 1 THEN 'Rescheduled'
                        WHEN LoanEndDate < GETDATE() THEN 'Overdue'
                        ELSE 'Active'
                    END
            """)
            loan_data = cursor.fetchall()

            if loan_data:
                statuses = [row.LoanStatus for row in loan_data]
                counts = [row.Count for row in loan_data]
                
                status_colors = []
                for s in statuses:
                    if s == 'Active': status_colors.append('#3498db')
                    elif s == 'Overdue': status_colors.append('#e67e22')
                    elif s == 'Defaulted': status_colors.append('#e74c3c')
                    elif s == 'Rescheduled': status_colors.append('#9b59b6')
                    else: status_colors.append('gray')

                fig_bar = plt.Figure(figsize=(4, 4), facecolor='#1e1e1e')
                ax_bar = fig_bar.add_subplot(111)
                ax_bar.bar(statuses, counts, color=status_colors)
                ax_bar.set_title("Current Loan Portfolio Status", color='white', fontweight='bold')
                ax_bar.set_ylabel("Number of Loans")
                ax_bar.tick_params(colors='white')
                
                # Make background invisible so it blends perfectly
                ax_bar.set_facecolor('#1e1e1e')
                for spine in ax_bar.spines.values():
                    spine.set_color('#333333')

                canvas_bar = FigureCanvasTkAgg(fig_bar, master=chart_frame)
                canvas_bar.draw()
                canvas_bar.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10)

        except Exception as e:
            print(f"Dashboard Error: {e}")
            ctk.CTkLabel(self.main_frame, text=f"Error loading dashboard stats: {e}", text_color="red").pack(pady=20)

    # ==================== CUSTOMER PROFILE POPUP ====================
    def show_customer_profile(self, customer_id, name):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Full Profile: {name}")
        # Increased height from 550 to 700 to fit the loans list
        popup.geometry("500x700")
        popup.attributes("-topmost", True) 
        
        ctk.CTkLabel(popup, text="Complete Customer Profile", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=f"{name} | Customer ID: {customer_id}", text_color="gray").pack(pady=(0, 10))
        
        if not self.db_conn: return
        
        try:
            cursor = self.db_conn.cursor()
            # 1. Fetch EVERYTHING from the Customer table
            cursor.execute("""
                SELECT CNIC, PhoneNumber, Email, Address, EmploymentStatus, MonthlyIncome, CreditScore, DateRegistered
                FROM CUSTOMER WHERE CustomerID = ?
            """, (customer_id,))
            cust = cursor.fetchone()
            
            # 2. Fetch the total amount they have borrowed across all loans
            cursor.execute("SELECT ISNULL(SUM(ApprovedAmount), 0) FROM LOAN WHERE CustomerID = ?", (customer_id,))
            total_loan = cursor.fetchone()[0]
            
            if cust:
                info_frame = ctk.CTkFrame(popup, fg_color="#2b2b2b", corner_radius=10)
                info_frame.pack(pady=10, padx=30, fill="x") # Changed from fill="both", expand=True so it doesn't hog space
                
                # Prepare data to loop through and draw
                details = [
                    ("CNIC:", cust.CNIC),
                    ("Phone:", cust.PhoneNumber),
                    ("Email:", cust.Email),
                    ("Address:", cust.Address),
                    ("Employment:", cust.EmploymentStatus),
                    ("Monthly Income:", f"Rs. {cust.MonthlyIncome:,.0f}" if cust.MonthlyIncome else "N/A"),
                    ("Registered On:", cust.DateRegistered.strftime("%Y-%m-%d") if cust.DateRegistered else "N/A"),
                    ("Total Borrowed:", f"Rs. {total_loan:,.0f}"),
                ]
                
                # Draw the labels dynamically
                for i, (label, val) in enumerate(details):
                    ctk.CTkLabel(info_frame, text=label, font=ctk.CTkFont(weight="bold")).grid(row=i, column=0, sticky="w", padx=20, pady=8)
                    ctk.CTkLabel(info_frame, text=str(val)).grid(row=i, column=1, sticky="w", padx=10, pady=8)
                
                # Highlight the Credit Score
                score_color = "#2ecc71" if cust.CreditScore and cust.CreditScore > 700 else "#e74c3c"
                ctk.CTkLabel(info_frame, text="Credit Score:", font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, sticky="w", padx=20, pady=8)
                ctk.CTkLabel(info_frame, text=str(cust.CreditScore), text_color=score_color, font=ctk.CTkFont(weight="bold")).grid(row=8, column=1, sticky="w", padx=10, pady=8)

            # ==================== NEW: ACTIVE LOANS LIST ====================
            cursor.execute("SELECT LoanID, ApprovedAmount, LoanStartDate FROM LOAN WHERE CustomerID = ?", (customer_id,))
            loans = cursor.fetchall()

            if loans:
                ctk.CTkLabel(popup, text="Active Loans", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
                
                loans_frame = ctk.CTkScrollableFrame(popup, fg_color="#1e1e1e", height=120)
                loans_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))
                
                for loan in loans:
                    row_frame = ctk.CTkFrame(loans_frame, fg_color="#333333", height=35)
                    row_frame.pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(row_frame, text=f"Loan #{loan.LoanID}", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
                    ctk.CTkLabel(row_frame, text=f"Rs {loan.ApprovedAmount:,.0f}").pack(side="left", padx=10)
                    
                    # The button that passes the specific LoanID to your EMI viewer!
                    btn_emi = ctk.CTkButton(row_frame, text="View EMI", width=80, fg_color="#8e44ad", hover_color="#9b59b6",
                                            command=lambda lid=loan.LoanID: self.show_emi_schedule(lid))
                    btn_emi.pack(side="right", padx=10)
            else:
                ctk.CTkLabel(popup, text="No active loans found for this customer.", text_color="gray").pack(pady=20)
                
        except Exception as e:
            print(f"Profile DB Error: {e}")
            ctk.CTkLabel(popup, text="Error loading details.", text_color="red").pack(pady=20)
            
        ctk.CTkButton(popup, text="Close Window", command=popup.destroy, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=15)
                         

    # ==================== CUSTOMER CRM ====================
    def show_customers(self):
        self.clear_main_frame()
        
       # --- 1. Header & Button Area ---
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Customer CRM", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        
        # Original: Add Customer Button (Green)
        btn_add = ctk.CTkButton(header_frame, text="+ Add New Customer", fg_color="#27ae60", hover_color="#2ecc71",
                                font=ctk.CTkFont(weight="bold"), command=self.open_add_customer_window)
        btn_add.pack(side="right", padx=5)

        # NEW: Issue Loan Button (Blue)
        btn_loan = ctk.CTkButton(header_frame, text="🏦 Issue New Loan", fg_color="#2980b9", hover_color="#3498db", 
                                 font=ctk.CTkFont(weight="bold"), command=self.open_loan_application)
        btn_loan.pack(side="right", padx=5)

        # --- 2. Search Bar Area ---
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.cust_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Name, CNIC, or Phone...", width=400, height=40)
        self.cust_search_entry.pack(side="left", padx=(0, 10))
        self.cust_search_entry.bind("<Return>", lambda event: self.execute_customer_search())
        
        btn_search = ctk.CTkButton(search_frame, text="Search 🔍", width=100, height=40, command=self.execute_customer_search)
        btn_search.pack(side="left")

        # --- 3. Results List Frame ---
        self.cust_list = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1e1e1e")
        self.cust_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.execute_customer_search(default_view=True)

    
    def open_loan_application(self):
        loan_window = ctk.CTkToplevel(self)
        loan_window.title("Loan Origination System")
        loan_window.geometry("450x450")
        loan_window.attributes('-topmost', True)
        
        ctk.CTkLabel(loan_window, text="Apply for New Loan", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(loan_window, text="SQL Stored Procedure Engine", text_color="#f39c12", font=ctk.CTkFont(size=12)).pack(pady=(0, 20))

        # Inputs
        ctk.CTkLabel(loan_window, text="Customer ID:").pack(anchor="w", padx=40)
        entry_cust_id = ctk.CTkEntry(loan_window, placeholder_text="e.g., 105", width=370)
        entry_cust_id.pack(pady=(0, 15), padx=40)

        ctk.CTkLabel(loan_window, text="Requested Amount (Rs):").pack(anchor="w", padx=40)
        entry_amount = ctk.CTkEntry(loan_window, placeholder_text="e.g., 500000", width=370)
        entry_amount.pack(pady=(0, 15), padx=40)

        ctk.CTkLabel(loan_window, text="Duration (Months):").pack(anchor="w", padx=40)
        entry_duration = ctk.CTkEntry(loan_window, placeholder_text="e.g., 12", width=370)
        entry_duration.pack(pady=(0, 20), padx=40)

        result_label = ctk.CTkLabel(loan_window, text="", font=ctk.CTkFont(weight="bold"))
        result_label.pack(pady=5)

        def process_application():
            try:
                cust_id = int(entry_cust_id.get())
                amount = float(entry_amount.get())
                duration = int(entry_duration.get())
                
                cursor = self.db_conn.cursor()
                
                # --- LETTING SQL DO THE WORK ---
                cursor.execute("EXEC sp_Apply_For_Loan @CustomerID=?, @RequestedAmount=?, @DurationMonths=?", 
                               (cust_id, amount, duration))
                
                result = cursor.fetchone()
                self.db_conn.commit()
                
                if result:
                    status = getattr(result, 'Status', 'ERROR')
                    message = getattr(result, 'Message', 'Unknown error.')
                    
                    if status == "APPROVED":
                        result_label.configure(text=f"✅ {status}\n{message}", text_color="#2ecc71")
                        entry_amount.delete(0, 'end')
                        entry_duration.delete(0, 'end')
                    else:
                        result_label.configure(text=f"❌ {status}\n{message}", text_color="#e74c3c")
                    
            except ValueError:
                result_label.configure(text="⚠️ Please enter valid numbers in all fields.", text_color="#f1c40f")
            except Exception as e:
                result_label.configure(text=f"Database Error:\n{str(e)}", text_color="#e74c3c")

        # Submit Button
        ctk.CTkButton(loan_window, text="Run Analysis & Apply", height=40, font=ctk.CTkFont(weight="bold"), command=process_application).pack(pady=10, padx=40, fill="x")
 

    def show_emi_schedule(self, loan_id):
        emi_window = ctk.CTkToplevel(self)
        emi_window.title(f"EMI Schedule - Loan #{loan_id}")
        emi_window.geometry("550x500")
        emi_window.attributes('-topmost', True)

        ctk.CTkLabel(emi_window, text=f"Repayment Schedule (Loan ID: {loan_id})", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Table Header
        header_frame = ctk.CTkFrame(emi_window, fg_color="#333333", height=30)
        header_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(header_frame, text="Inst. #", width=50, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Due Date", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="EMI Amount", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Status", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

        # Scrollable List
        list_frame = ctk.CTkScrollableFrame(emi_window, fg_color="#1e1e1e")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        try:
            cursor = self.db_conn.cursor()
            # Fetch the EMIs we just generated!
            cursor.execute("""
                SELECT InstallmentNumber, DueDate, ScheduledAmount, PaymentMethod 
                FROM PAYMENT 
                WHERE LoanID = ? 
                ORDER BY InstallmentNumber
            """, (loan_id,))
            
            rows = cursor.fetchall()

            if not rows:
                ctk.CTkLabel(list_frame, text="No EMI schedule found.", text_color="gray").pack(pady=20)
                return

            for row in rows:
                row_frame = ctk.CTkFrame(list_frame, fg_color="#2b2b2b", height=35)
                row_frame.pack(fill="x", pady=2)
                
                # Safely format the date
                due_date = row.DueDate.strftime('%Y-%m-%d') if row.DueDate else "N/A"
                
                ctk.CTkLabel(row_frame, text=row.InstallmentNumber, width=50).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=due_date, width=120).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"Rs {row.ScheduledAmount:,.2f}", width=120).pack(side="left", padx=10)
                
                # Make 'Pending' yellow, and paid items green
                status_color = "#f1c40f" if row.PaymentMethod == "Pending" else "#2ecc71"
                ctk.CTkLabel(row_frame, text=row.PaymentMethod, width=100, text_color=status_color).pack(side="left", padx=10)

        except Exception as e:
            ctk.CTkLabel(list_frame, text=f"Error loading schedule:\n{e}", text_color="#e74c3c").pack(pady=20)


    def execute_customer_search(self, default_view=False):
        for widget in self.cust_list.winfo_children():
            widget.destroy()

        if not self.db_conn: return

        search_term = "" if default_view else self.cust_search_entry.get().strip()
        
        try:
            cursor = self.db_conn.cursor()
            if default_view or not search_term:
                cursor.execute("SELECT TOP 15 CustomerID, FirstName, LastName, CNIC, PhoneNumber, CreditScore FROM CUSTOMER ORDER BY CustomerID DESC")
            # Inside your execute_customer_search function:
            else:
                query = """
                SELECT CustomerID, FirstName, LastName, CNIC, PhoneNumber, CreditScore 
                FROM CUSTOMER 
                WHERE (FirstName + ' ' + LastName) LIKE ? 
                OR CNIC LIKE ? 
                OR PhoneNumber LIKE ?
                OR (CAST(CustomerID AS VARCHAR) = ? AND ? <> '')
                """
                wild = f"%{search_term}%"
                # We pass search_term twice: once for the comparison, once for the empty check
                cursor.execute(query, (wild, wild, wild, search_term, search_term))
                
            rows = cursor.fetchall()
            
            if not rows:
                ctk.CTkLabel(self.cust_list, text="No customers found.", text_color="gray").pack(pady=40)
                return

            # ... (the rest of your UI building code stays exactly the same)
            header = ctk.CTkFrame(self.cust_list, fg_color="#333333", height=40)
            header.pack(fill="x", padx=10, pady=(0, 5))
            ctk.CTkLabel(header, text="ID", width=50, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="Name", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="CNIC", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="Phone", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            
            for row in rows:
                row_frame = ctk.CTkFrame(self.cust_list, fg_color="#2b2b2b", height=45)
                row_frame.pack(fill="x", padx=10, pady=2)
                full_name = f"{row.FirstName} {row.LastName}"
                ctk.CTkLabel(row_frame, text=row.CustomerID, width=50).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=full_name, width=180, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=row.CNIC, width=150).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=row.PhoneNumber, width=120).pack(side="left", padx=10)
                
                btn_view = ctk.CTkButton(row_frame, text="View Profile", width=100, fg_color="#2980b9", hover_color="#3498db", 
                                         command=lambda cid=row.CustomerID, n=full_name: self.show_customer_profile(cid, n))
                btn_view.pack(side="right", padx=10)
                
        except Exception as e:
            print(f"Customer Search Error: {e}")

    def open_add_customer_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Register New Customer")
        popup.geometry("500x650")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Customer Onboarding", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        form_frame = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=5)

        entries = {}
        fields = [
            ("First Name:", "FirstName"), ("Last Name:", "LastName"), 
            ("CNIC (e.g. 12345-1234567-1):", "CNIC"), ("Phone Number:", "PhoneNumber"), 
            ("Email Address:", "Email"), ("Physical Address:", "Address"),
            ("Employment Status (e.g. Salaried, Business):", "EmploymentStatus"), 
            ("Monthly Income (Rs.):", "MonthlyIncome"), ("Credit Score (300-850):", "CreditScore")
        ]

        for label_text, key in fields:
            ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form_frame, width=400)
            entry.pack(fill="x", pady=(0, 5))
            entries[key] = entry

        status_label = ctk.CTkLabel(popup, text="", text_color="red")
        status_label.pack(pady=5)

        def save_customer():
            data = {k: v.get().strip() for k, v in entries.items()}
            
            if not all(data.values()):
                status_label.configure(text="⚠️ Please fill in all fields.", text_color="#e74c3c")
                return
                
            try:
                income = float(data["MonthlyIncome"])
                score = int(data["CreditScore"])
                
                if not (300 <= score <= 850):
                    status_label.configure(text="⚠️ Credit Score must be between 300 and 850.", text_color="#e74c3c")
                    return

                cursor = self.db_conn.cursor()
                query = """
                EXEC sp_Add_Customer 
                    @CNIC=?, @FirstName=?, @LastName=?, @PhoneNumber=?, 
                    @Email=?, @Address=?, @EmploymentStatus=?, @MonthlyIncome=?, @CreditScore=?
                """
                cursor.execute(query, (
                    data["CNIC"], data["FirstName"], data["LastName"], data["PhoneNumber"], 
                    data["Email"], data["Address"], data["EmploymentStatus"], income, score
                ))
                
                result = cursor.fetchone()
                self.db_conn.commit()
                
                new_id = result[0] if result else "Unknown"
                print(f"Success! New Customer ID: {new_id}")
                
                self.execute_customer_search() 
                popup.destroy()
                
            except Exception as e:
                print(f"Database Error: {e}")
                status_label.configure(text="❌ Error: Check for duplicate CNIC/Email or invalid data.", text_color="#e74c3c")

        btn_save = ctk.CTkButton(popup, text="Save Customer Record", fg_color="#27ae60", hover_color="#2ecc71", 
                                 height=40, font=ctk.CTkFont(weight="bold"), command=save_customer)
        btn_save.pack(fill="x", padx=40, pady=(10, 20))

    # ==================== LOAN SEARCH & RISK BOARD ====================
    def show_loans(self):
        self.clear_main_frame()
        
        label = ctk.CTkLabel(self.main_frame, text="FinCore | Loan Risk & Search", font=ctk.CTkFont(size=28, weight="bold"))
        label.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")

        self.loan_search_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Search Customer Name for Loan Status...", width=350, height=35)
        self.loan_search_entry.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.loan_search_entry.bind("<Return>", lambda event: self.execute_loan_search())

        btn_search = ctk.CTkButton(self.main_frame, text="Search Loans 🔍", width=120, height=35, command=self.execute_loan_search)
        btn_search.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.loans_list = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1e1e1e")
        self.loans_list.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
        
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.execute_loan_search(default_view=True)

    def execute_loan_search(self, default_view=False):
        for widget in self.loans_list.winfo_children():
            widget.destroy()

        if not self.db_conn: return

        search_term = "" if default_view else self.loan_search_entry.get().strip()
        if not default_view and not search_term: return

        cursor = self.db_conn.cursor()
        try:
            if default_view:
                ctk.CTkLabel(self.loans_list, text="⚠️ High Risk Portfolio (Top 15 Defaulted Accounts)", text_color="#e74c3c", font=ctk.CTkFont(weight="bold")).pack(pady=(0,10), anchor="w", padx=10)
                query = """
                SELECT TOP 15 L.LoanID, C.FirstName + ' ' + C.LastName as FullName, L.ApprovedAmount,
                       'Defaulted' AS CalculatedStatus
                FROM LOAN L
                JOIN CUSTOMER C ON L.CustomerID = C.CustomerID
                WHERE L.ReasonForDefault IS NOT NULL 
                  AND L.ReasonForDefault NOT IN ('', ' ', 'NULL', 'None', '0')
                ORDER BY L.ApprovedAmount DESC
                """
                cursor.execute(query)
            else:
                query = """
                SELECT L.LoanID, C.FirstName + ' ' + C.LastName as FullName, L.ApprovedAmount,
                       CASE 
                           WHEN L.ReasonForDefault IS NOT NULL AND L.ReasonForDefault NOT IN ('', ' ', 'NULL', 'None', '0') THEN 'Defaulted'
                           WHEN L.IsRescheduled = 1 THEN 'Rescheduled'
                           WHEN L.LoanEndDate < GETDATE() THEN 'Overdue'
                           ELSE 'Active'
                       END AS CalculatedStatus
                FROM LOAN L
                JOIN CUSTOMER C ON L.CustomerID = C.CustomerID
                WHERE (C.FirstName + ' ' + C.LastName) LIKE ?
                """
                wildcard = f"%{search_term}%"
                cursor.execute(query, (wildcard,))

            rows = cursor.fetchall()

            if not rows:
                msg = "No high-risk loans found." if default_view else f"No loans found for '{search_term}'"
                ctk.CTkLabel(self.loans_list, text=msg, text_color="gray").pack(pady=50)
                return

            header = ctk.CTkFrame(self.loans_list, fg_color="#333333", height=40)
            header.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkLabel(header, text="ID", width=50, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="Customer", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="Amount", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="Status", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(header, text="Action", width=100, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=20)

            for loan in rows:
                row_frame = ctk.CTkFrame(self.loans_list, fg_color="#2b2b2b", height=45)
                row_frame.pack(fill="x", padx=10, pady=2)

                status_color = "#2ecc71" 
                if loan.CalculatedStatus in ['Overdue', 'Defaulted']: status_color = "#e74c3c" 
                elif loan.CalculatedStatus == 'Rescheduled': status_color = "#f39c12" 

                ctk.CTkLabel(row_frame, text=f"#{loan.LoanID}", width=50).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=loan.FullName, width=180, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"Rs. {loan.ApprovedAmount:,.0f}", width=120).pack(side="left", padx=10)
                
                status_badge = ctk.CTkLabel(row_frame, text=loan.CalculatedStatus.upper(), text_color=status_color, font=ctk.CTkFont(size=11, weight="bold"), width=100)
                status_badge.pack(side="left", padx=10)
                
                btn_history = ctk.CTkButton(
                    row_frame, text="History 📜", width=80, fg_color="#8e44ad", hover_color="#9b59b6",
                    command=lambda lid=loan.LoanID, name=loan.FullName: self.open_history_window(lid, name)
                )
                btn_history.pack(side="right", padx=10)

        except Exception as e:
            print(f"SQL Error: {e}")

    
    # ==================== CUSTOMER ANALYTICS (PAGINATED) ====================
    def show_risk_management(self):
        self.clear_main_frame()
        # 1. Header renamed to reflect both good (Prime) and bad (Defaulters) data
        label = ctk.CTkLabel(self.main_frame, text="FinCore | Customer Analytics", font=ctk.CTkFont(size=28, weight="bold"))
        label.pack(pady=(20, 10), padx=20, anchor="w")

        if not self.db_conn:
            ctk.CTkLabel(self.main_frame, text="🔴 Database Not Connected", text_color="red").pack(pady=20)
            return

        # --- Set up the Tabs ---
        tabview = ctk.CTkTabview(self.main_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 2. Added the Prime tab
        tab_prime = tabview.add("Prime Customers") 
        tab_watchlist = tabview.add("Defaulter Watchlist")
        tab_risk = tabview.add("Risk Classification")

        # --- Set up the Scrollable Frames ---
        # 3. Added the Prime scrollable frame
        scroll_prime = ctk.CTkScrollableFrame(tab_prime, fg_color="transparent")
        scroll_prime.pack(fill="both", expand=True)

        scroll_watchlist = ctk.CTkScrollableFrame(tab_watchlist, fg_color="transparent")
        scroll_watchlist.pack(fill="both", expand=True)

        scroll_risk = ctk.CTkScrollableFrame(tab_risk, fg_color="transparent")
        scroll_risk.pack(fill="both", expand=True)

        # --- Pagination Trackers ---
        self.prime_offset = 0  # 4. Added Prime tracker
        self.watchlist_offset = 0
        self.risk_offset = 0
        self.load_limit = 50

        # --- The "Load More" Buttons ---
        btn_more_prime = ctk.CTkButton(scroll_prime, text="Load More", command=lambda: load_prime_batch()) # 5. Added Prime button
        btn_more_watchlist = ctk.CTkButton(scroll_watchlist, text="Load More", command=lambda: load_watchlist_batch())
        btn_more_risk = ctk.CTkButton(scroll_risk, text="Load More", command=lambda: load_risk_batch())


        # ==========================================
        # 0. PRIME CUSTOMERS BATCH LOADER (THE GOOD)
        # ==========================================
        def load_prime_batch():
            try:
                cursor = self.db_conn.cursor()
                # Query the raw CUSTOMER table, sorting by highest credit score first
                query = f"""
                    SELECT CustomerID, FirstName, LastName, CreditScore, MonthlyIncome 
                    FROM CUSTOMER 
                    ORDER BY CreditScore DESC 
                    OFFSET {self.prime_offset} ROWS 
                    FETCH NEXT {self.load_limit} ROWS ONLY
                """
                cursor.execute(query)
                records = cursor.fetchall()
                
                if not records:
                    btn_more_prime.configure(text="No More Records", state="disabled")
                    return

                btn_more_prime.pack_forget()

                for row in records:
                    # --- EYE-CATCHING PRIME CARD (Gold Theme) ---
                    card = ctk.CTkFrame(scroll_prime, fg_color="#2b2b2b", corner_radius=10, border_width=1, border_color="#f1c40f")
                    card.pack(fill="x", pady=8, padx=10)
                    
                    # Left Side: Name & Premium Tag
                    info_frame = ctk.CTkFrame(card, fg_color="transparent")
                    info_frame.pack(side="left", padx=15, pady=10, fill="x", expand=True)
                    
                    ctk.CTkLabel(info_frame, text=f"🌟 {row.FirstName} {row.LastName}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
                    ctk.CTkLabel(info_frame, text="STATUS: PRIME / PRE-APPROVED", text_color="#f1c40f", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(2, 0))

                    # Right Side: Credit Score & Income
                    stats_frame = ctk.CTkFrame(card, fg_color="transparent")
                    stats_frame.pack(side="right", padx=20, pady=10)
                    
                    ctk.CTkLabel(stats_frame, text=f"Income: Rs. {row.MonthlyIncome:,.2f}", text_color="#a4b0be", font=ctk.CTkFont(size=12)).pack(anchor="e")
                    ctk.CTkLabel(stats_frame, text=f"Score: {row.CreditScore}", text_color="#2ecc71", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="e")
                    # ----------------------------------------

                self.prime_offset += self.load_limit
                
                if len(records) == self.load_limit:
                    btn_more_prime.pack(pady=20)
                else:
                    btn_more_prime.configure(text="End of List", state="disabled")
                    btn_more_prime.pack(pady=20)

            except Exception as e:
                print(f"Prime Load Error: {e}")


        # ==========================================
        # 1. WATCHLIST BATCH LOADER
        # ==========================================
        def load_watchlist_batch():
            try:
                cursor = self.db_conn.cursor()
                # SQL Server Pagination Query
                query = f"""
                    SELECT * FROM vw_Defaulter_Watchlist 
                    ORDER BY TotalFines DESC 
                    OFFSET {self.watchlist_offset} ROWS 
                    FETCH NEXT {self.load_limit} ROWS ONLY
                """
                cursor.execute(query)
                records = cursor.fetchall()
                
                # If no more records exist, disable the button
                if not records:
                    btn_more_watchlist.configure(text="No More Records", state="disabled")
                    return

                # Temporarily remove the button from the screen so we can append new rows above it
                btn_more_watchlist.pack_forget()

                for row in records:
                    # --- EYE-CATCHING WATCHLIST CARD ---
                    # Card background with a red border to indicate danger/default
                    card = ctk.CTkFrame(scroll_watchlist, fg_color="#2b2b2b", corner_radius=10, border_width=1, border_color="#c0392b")
                    card.pack(fill="x", pady=8, padx=10)
                    
                    # Left Side: Name & Default Status
                    info_frame = ctk.CTkFrame(card, fg_color="transparent")
                    info_frame.pack(side="left", padx=15, pady=10, fill="x", expand=True)
                    
                    ctk.CTkLabel(info_frame, text=f"👤 {row.DefaulterName}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
                    
                    # Bold red defaulted tag
                    ctk.CTkLabel(info_frame, text="⚠️ STATUS: ACCOUNT DEFAULTED", text_color="#ff4757", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(2, 0))

                    # Right Side: Fines Amount
                    fine_frame = ctk.CTkFrame(card, fg_color="transparent")
                    fine_frame.pack(side="right", padx=20, pady=10)
                    
                    ctk.CTkLabel(fine_frame, text="Total Fines Due", text_color="#a4b0be", font=ctk.CTkFont(size=12)).pack(anchor="e")
                    ctk.CTkLabel(fine_frame, text=f"Rs. {row.TotalFines:,.2f}", text_color="#ffa502", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="e")
                    # ----------------------------------------

                # Update the tracker (we loaded 50, so next time skip 50)
                self.watchlist_offset += self.load_limit
                
                # Slap the "Load More" button back at the very bottom
                if len(records) == self.load_limit:
                    btn_more_watchlist.pack(pady=20)
                else:
                    btn_more_watchlist.configure(text="End of List", state="disabled")
                    btn_more_watchlist.pack(pady=20)

            except Exception as e:
                print(f"Watchlist Load Error: {e}")

        # ==========================================
        # RISK CLASSIFICATION BATCH LOADER
        # ==========================================
        def load_risk_batch():
            try:
                cursor = self.db_conn.cursor()
                
                # BYPASS THE VIEW: Query CUSTOMER table directly so we know exactly what columns we have!
                query = f"""
                    SELECT 
                        FirstName, 
                        LastName, 
                        CreditScore,
                        CASE 
                            WHEN CreditScore < 500 THEN 'HIGH RISK'
                            ELSE 'MODERATE RISK'
                        END AS RiskLevel
                    FROM CUSTOMER 
                    WHERE CreditScore < 600
                    ORDER BY CreditScore ASC 
                    OFFSET {self.risk_offset} ROWS 
                    FETCH NEXT {self.load_limit} ROWS ONLY
                """
                cursor.execute(query)
                records = cursor.fetchall()
                
                if not records:
                    btn_more_risk.configure(text="No More Records", state="disabled")
                    return

                btn_more_risk.pack_forget()

                for row in records:
                    # We now 100% guarantee these columns exist because of our direct query above
                    cust_name = f"{row.FirstName} {row.LastName}"
                    risk_level = row.RiskLevel
                    
                    if 'HIGH' in risk_level.upper():
                        border_color = "#e74c3c" # Red
                        text_color = "#ff4757"
                    elif 'LOW' in risk_level.upper():
                        border_color = "#2ecc71" # Green
                        text_color = "#2ed573"
                    else:
                        border_color = "#f39c12" # Yellow/Orange
                        text_color = "#ffa502"

                    # --- EYE-CATCHING RISK CARD ---
                    card = ctk.CTkFrame(scroll_risk, fg_color="#2b2b2b", corner_radius=10, border_width=1, border_color=border_color)
                    card.pack(fill="x", pady=8, padx=10)
                    
                    # Left Side: Name & Risk Level
                    info_frame = ctk.CTkFrame(card, fg_color="transparent")
                    info_frame.pack(side="left", padx=15, pady=10, fill="x", expand=True)
                    
                    ctk.CTkLabel(info_frame, text=f"👤 {cust_name}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
                    ctk.CTkLabel(info_frame, text=f"Risk Classification: {risk_level.upper()}", text_color=text_color, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(2, 0))

                    # Right Side: Credit Score
                    score_frame = ctk.CTkFrame(card, fg_color="transparent")
                    score_frame.pack(side="right", padx=20, pady=10)
                    
                    ctk.CTkLabel(score_frame, text="Credit Score", text_color="#a4b0be", font=ctk.CTkFont(size=12)).pack(anchor="e")
                    ctk.CTkLabel(score_frame, text=f"{row.CreditScore}", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="e")
                    # ----------------------------------------

                self.risk_offset += self.load_limit
                
                if len(records) == self.load_limit:
                    btn_more_risk.pack(pady=20)
                else:
                    btn_more_risk.configure(text="End of List", state="disabled")
                    btn_more_risk.pack(pady=20)

            except Exception as e:
                print(f"Risk Load Error: {e}")


        # --- Fire the first batches when the tab opens! ---
        load_prime_batch()
        load_watchlist_batch()
        load_risk_batch()

    def open_forgive_fine_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Forgive Late Fines")
        popup.geometry("350x250")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Pardon Customer Fines", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(popup, text="Enter the Target Loan ID:").pack(pady=(10, 0))
        
        entry_loan_id = ctk.CTkEntry(popup, width=200, placeholder_text="e.g. 15")
        entry_loan_id.pack(pady=10)
        
        status_label = ctk.CTkLabel(popup, text="", text_color="red")
        status_label.pack()

        def submit_forgive():
            try:
                loan_id = int(entry_loan_id.get().strip())
                cursor = self.db_conn.cursor()
                
                # Execute your stored procedure!
                cursor.execute("EXEC sp_ForgiveLateFines @TargetLoanID=?", (loan_id,))
                self.db_conn.commit()
                
                print(f"Fines forgiven for Loan {loan_id}")
                self.show_risk_management() # Refresh the tabs to see fines drop to 0!
                popup.destroy()
            except ValueError:
                status_label.configure(text="Please enter a valid number.")
            except Exception as e:
                status_label.configure(text=f"DB Error: {e}")

        ctk.CTkButton(popup, text="Execute Procedure", fg_color="#27ae60", hover_color="#2ecc71", command=submit_forgive).pack(pady=10)

    # ==================== LEDGER / HISTORY ====================
    def open_history_window(self, loan_id, customer_name):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Financial Ledger: {customer_name}")
        popup.geometry("650x550") 
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Loan Ledger & Payment Receipts", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(popup, text=f"{customer_name} | Loan #{loan_id}", text_color="gray").pack(pady=(0, 10))
        
        if not self.db_conn: return

        try:
            cursor = self.db_conn.cursor()
            
            # --- 1. THE MATH: Calculate the exact financial standing ---
            query_summary = """
            SELECT 
                L.ApprovedAmount, 
                L.LoanStartDate, 
                L.LoanEndDate, 
                L.IsRescheduled,
                L.ReasonForDefault,
                ISNULL((SELECT SUM(PaymentAmount) FROM PAYMENT WHERE LoanID = L.LoanID), 0) AS TotalPaid
            FROM LOAN L
            WHERE L.LoanID = ?
            """
            cursor.execute(query_summary, (loan_id,))
            loan_info = cursor.fetchone()
            
            if loan_info:
                summary_frame = ctk.CTkFrame(popup, fg_color="#2b2b2b")
                summary_frame.pack(fill="x", padx=20, pady=10)
                
                start_date = loan_info.LoanStartDate.strftime("%Y-%m-%d")
                end_date = loan_info.LoanEndDate.strftime("%Y-%m-%d")
                
                total_paid = loan_info.TotalPaid
                remaining_balance = loan_info.ApprovedAmount - total_paid
                if remaining_balance < 0: remaining_balance = 0 
                
                row1 = ctk.CTkFrame(summary_frame, fg_color="transparent")
                row1.pack(fill="x", pady=(10, 5), padx=15)
                ctk.CTkLabel(row1, text=f"Approved: Rs. {loan_info.ApprovedAmount:,.0f}").pack(side="left", padx=(0, 15))
                ctk.CTkLabel(row1, text=f"Total Paid: Rs. {total_paid:,.0f}", text_color="#2ecc71").pack(side="left", padx=15)
                ctk.CTkLabel(row1, text=f"Remaining: Rs. {remaining_balance:,.0f}", text_color="#e74c3c" if remaining_balance > 0 else "white", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15)

                row2 = ctk.CTkFrame(summary_frame, fg_color="transparent")
                row2.pack(fill="x", pady=(0, 10), padx=15)
                ctk.CTkLabel(row2, text=f"Timeline: {start_date} to {end_date}").pack(side="left", padx=(0, 15))
                
                if loan_info.IsRescheduled:
                    ctk.CTkLabel(row2, text="🔄 LOAN RESCHEDULED", text_color="#f39c12", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15)

                if loan_info.ReasonForDefault and loan_info.ReasonForDefault not in ('', ' ', 'NULL', 'None', '0'):
                    row3 = ctk.CTkFrame(summary_frame, fg_color="transparent")
                    row3.pack(fill="x", pady=(0, 10), padx=15)
                    ctk.CTkLabel(row3, text=f"🚨 DEFAULTED: {loan_info.ReasonForDefault}", text_color="#c0392b", font=ctk.CTkFont(weight="bold")).pack(side="left")

            # --- 2. THE RECEIPTS ---
            history_list = ctk.CTkScrollableFrame(popup, fg_color="#1e1e1e", height=250)
            history_list.pack(pady=10, padx=20, fill="both", expand=True)
            
            query_payments = """
            SELECT InstallmentNumber, PaymentAmount, PaymentDate, PaymentMethod, LatePaymentFine
            FROM PAYMENT
            WHERE LoanID = ?
            ORDER BY PaymentDate DESC
            """
            cursor.execute(query_payments, (loan_id,))
            rows = cursor.fetchall()
            
            if not rows:
                ctk.CTkLabel(history_list, text="No payments have been made towards this loan yet.", text_color="gray").pack(pady=50)
                return
                
            header = ctk.CTkFrame(history_list, fg_color="#333333", height=30)
            header.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(header, text="Inst. #", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Date Paid", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Amount Paid", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Method", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Late Fine", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            for row in rows:
                row_frame = ctk.CTkFrame(history_list, fg_color="#2b2b2b", height=35)
                row_frame.pack(fill="x", pady=2)
                
                date_str = row.PaymentDate.strftime("%Y-%m-%d") if row.PaymentDate else "---"
                fine_str = f"Rs. {row.LatePaymentFine:,.0f}" if row.LatePaymentFine > 0 else "---"
                fine_color = "#e74c3c" if row.LatePaymentFine > 0 else "gray"
                
                ctk.CTkLabel(row_frame, text=f"{row.InstallmentNumber}", width=60).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=date_str, width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=f"Rs. {row.PaymentAmount:,.0f}", width=120, text_color="#2ecc71").pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=row.PaymentMethod, width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=fine_str, width=80, text_color=fine_color).pack(side="left", padx=5)
                
        except Exception as e:
            print(f"History SQL Error: {e}")
            ctk.CTkLabel(popup, text="Error loading ledger.", text_color="red").pack(pady=20)

    # ==================== PAYMENTS SECTION ====================
    def show_payments(self):
        self.clear_main_frame()
        
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Payment Processing", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        
        btn_process = ctk.CTkButton(header_frame, text="⚙️ Process Payment (SP)", fg_color="#2980b9", hover_color="#3498db",
                                    font=ctk.CTkFont(weight="bold"), command=self.open_process_payment_window)
        btn_process.pack(side="right")

        pay_list = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1e1e1e")
        pay_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.db_conn: return
        
        try:
            cursor = self.db_conn.cursor()
            query = """
            SELECT TOP 20 
                P.PaymentID, L.LoanID, C.FirstName + ' ' + C.LastName AS CustomerName,
                P.PaymentAmount, P.PaymentDate, P.PaymentMethod, P.LatePaymentFine
            FROM PAYMENT P
            JOIN LOAN L ON P.LoanID = L.LoanID
            JOIN CUSTOMER C ON L.CustomerID = C.CustomerID
            ORDER BY P.PaymentDate DESC, P.PaymentID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                ctk.CTkLabel(pay_list, text="No recent payments found.", text_color="gray").pack(pady=40)
                return

            header = ctk.CTkFrame(pay_list, fg_color="#333333", height=40)
            header.pack(fill="x", padx=10, pady=(0, 5))
            ctk.CTkLabel(header, text="Pay ID", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Customer", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Amount", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Date", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Method", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Fine", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            for row in rows:
                row_frame = ctk.CTkFrame(pay_list, fg_color="#2b2b2b", height=45)
                row_frame.pack(fill="x", padx=10, pady=2)
                
                date_str = row.PaymentDate.strftime("%Y-%m-%d") if row.PaymentDate else "---"
                fine_color = "#e74c3c" if row.LatePaymentFine > 0 else "white"
                
                ctk.CTkLabel(row_frame, text=f"#{row.PaymentID}", width=60).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=f"{row.CustomerName} (L-{row.LoanID})", width=180, anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=f"Rs. {row.PaymentAmount:,.0f}", width=120, text_color="#2ecc71").pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=date_str, width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=row.PaymentMethod, width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=f"Rs. {row.LatePaymentFine:,.0f}", width=80, text_color=fine_color).pack(side="left", padx=5)
                
        except Exception as e:
            print(f"Payment Load Error: {e}")

    def open_process_payment_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Process New Payment")
        popup.geometry("450x550")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="Record New Loan Payment", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))

        # --- STEP 1: Search by Customer ID ---
        search_frame = ctk.CTkFrame(popup, fg_color="transparent")
        search_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(search_frame, text="Customer ID:").pack(anchor="w")
        entry_cust_id = ctk.CTkEntry(search_frame, width=150, placeholder_text="e.g. 1")
        entry_cust_id.pack(side="left", padx=(0, 10))
        
        # We will store the fetched loans in this dictionary to access their hidden Loan IDs
        self.current_loans = {} 
        
        loan_dropdown = ctk.CTkOptionMenu(popup, width=370, values=["Fetch loans first..."])
        loan_dropdown.pack(pady=10)
        
        info_label = ctk.CTkLabel(popup, text="", justify="left", font=ctk.CTkFont(size=14))
        info_label.pack(pady=(5, 10))

        def fetch_customer_loans():
            try:
                cid = int(entry_cust_id.get().strip())
                cursor = self.db_conn.cursor()
                
                # Fetching the customer's loans and how much they have paid
                query = """
                SELECT 
                    L.LoanID,
                    C.FirstName + ' ' + C.LastName AS CustomerName,
                    L.ApprovedAmount,
                    ISNULL((SELECT SUM(PaymentAmount) FROM PAYMENT WHERE LoanID = L.LoanID), 0) AS TotalPaid
                FROM LOAN L
                JOIN CUSTOMER C ON L.CustomerID = C.CustomerID
                WHERE C.CustomerID = ?
                """
                cursor.execute(query, (cid,))
                loans = cursor.fetchall()
                
                if loans:
                    self.current_loans.clear()
                    dropdown_values = []
                    
                    for row in loans:
                        remaining = row.ApprovedAmount - row.TotalPaid
                        if remaining < 0: remaining = 0
                        
                        loan_str = f"Loan #{row.LoanID} - {row.CustomerName}"
                        dropdown_values.append(loan_str)
                        self.current_loans[loan_str] = {
                            "id": row.LoanID,
                            "remaining": remaining,
                            "total": row.ApprovedAmount,
                            "name": row.CustomerName
                        }
                        
                    loan_dropdown.configure(values=dropdown_values)
                    loan_dropdown.set(dropdown_values[0])
                    update_info_label(dropdown_values[0])
                else:
                    loan_dropdown.configure(values=["No active loans found."])
                    loan_dropdown.set("No active loans found.")
                    info_label.configure(text="❌ No loans exist for this Customer.", text_color="#e74c3c")
                    self.current_loans.clear()
            except Exception as e:
                info_label.configure(text=f"❌ DB Error: {e}", text_color="#e74c3c")

        def update_info_label(selected_loan_str):
            if selected_loan_str in self.current_loans:
                data = self.current_loans[selected_loan_str]
                info_text = (
                    f"👤 Customer: {data['name']}\n"
                    f"💰 Total Loan: Rs. {data['total']:,.0f}\n"
                    f"📉 Remaining Balance: Rs. {data['remaining']:,.0f}\n"
                    f"📅 Standard Monthly Installment: View Loan Terms" # Generic placeholder, you can map exact formulas here later if needed
                )
                info_label.configure(text=info_text, text_color="#3498db")

        # When the dropdown changes, update the text label automatically
        loan_dropdown.configure(command=update_info_label)

        ctk.CTkButton(search_frame, text="Fetch Loans", width=100, fg_color="#8e44ad", hover_color="#9b59b6", command=fetch_customer_loans).pack(side="left")

        # --- STEP 2: Enter Payment Details ---
        ctk.CTkLabel(popup, text="Amount Paid (Rs.):").pack(anchor="w", padx=40)
        entry_amount = ctk.CTkEntry(popup, width=370)
        entry_amount.pack(pady=(0, 10))

        ctk.CTkLabel(popup, text="Payment Method:").pack(anchor="w", padx=40)
        entry_method = ctk.CTkOptionMenu(popup, width=370, values=["Cash", "Bank Transfer", "Credit Card", "Cheque"])
        entry_method.pack(pady=(0, 20))

        status_label = ctk.CTkLabel(popup, text="", text_color="red")
        status_label.pack()

        def submit_payment():
            selected = loan_dropdown.get()
            if selected not in self.current_loans:
                status_label.configure(text="⚠️ Please select a valid loan first.")
                return
                
            try:
                # We pull the hidden Loan ID from the dictionary!
                lid = self.current_loans[selected]["id"]
                amt = float(entry_amount.get().strip())
                meth = entry_method.get()

                cursor = self.db_conn.cursor()
                cursor.execute("EXEC sp_Process_Payment @LoanID=?, @AmountPaid=?, @Method=?", (lid, amt, meth))
                self.db_conn.commit()

                print(f"Payment applied to Loan {lid} successfully.")
                popup.destroy()
            except ValueError:
                status_label.configure(text="⚠️ Please fill in a valid number amount.")
            except Exception as e:
                status_label.configure(text=f"DB Error: {e}")

        ctk.CTkButton(popup, text="Record Payment", fg_color="#27ae60", hover_color="#2ecc71", width=370, command=submit_payment).pack(pady=10)

    # ==================== AUDIT LOG SECTION ====================
    def show_audit(self):
        self.clear_main_frame()
        
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Security & Audit Logs", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        ctk.CTkLabel(header_frame, text="Powered by SQL Triggers", text_color="#f39c12", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

        log_list = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1e1e1e")
        log_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.db_conn: return

        # Static Header Row
        header = ctk.CTkFrame(log_list, fg_color="#333333", height=40)
        header.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkLabel(header, text="Log ID", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Date/Time", width=140, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Action Performed", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Table (Rec ID)", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Old Value", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="New Value", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        # Pagination Trackers
        self.audit_offset = 0
        self.load_limit = 50
        btn_more_audit = ctk.CTkButton(log_list, text="Load More", command=lambda: load_audit_batch())

        def load_audit_batch():
            try:
                cursor = self.db_conn.cursor()
                query = f"""
                    SELECT LogID, TableName, ActionType, RecordID, ActionDate, OldValue, NewValue 
                    FROM AUDIT_LOG 
                    ORDER BY ActionDate DESC 
                    OFFSET {self.audit_offset} ROWS 
                    FETCH NEXT {self.load_limit} ROWS ONLY
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if not rows and self.audit_offset == 0:
                    ctk.CTkLabel(log_list, text="Audit Log is clean. No unauthorized changes detected.", text_color="#2ecc71").pack(pady=40)
                    return
                elif not rows:
                    btn_more_audit.configure(text="No More Records", state="disabled")
                    return

                btn_more_audit.pack_forget()

                for row in rows:
                    row_frame = ctk.CTkFrame(log_list, fg_color="#2b2b2b", height=45)
                    row_frame.pack(fill="x", padx=10, pady=2)
                    
                    date_str = row.ActionDate.strftime("%Y-%m-%d %H:%M") if row.ActionDate else "---"
                    old_val = str(row.OldValue)[:15] + "..." if row.OldValue and len(str(row.OldValue)) > 15 else (row.OldValue if row.OldValue else "NULL")
                    new_val = str(row.NewValue)[:15] + "..." if row.NewValue and len(str(row.NewValue)) > 15 else (row.NewValue if row.NewValue else "NULL")
                    
                    ctk.CTkLabel(row_frame, text=f"#{row.LogID}", width=60).pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=date_str, width=140).pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=row.ActionType, width=180, anchor="w", text_color="#f39c12").pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=f"{row.TableName} ({row.RecordID})", width=120).pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=old_val, width=100, text_color="#e74c3c").pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=new_val, width=100, text_color="#2ecc71").pack(side="left", padx=5)

                self.audit_offset += self.load_limit
                
                if len(rows) == self.load_limit:
                    btn_more_audit.pack(pady=20)
                else:
                    btn_more_audit.configure(text="End of Log", state="disabled")
                    btn_more_audit.pack(pady=20)

            except Exception as e:
                print(f"Audit Log Error: {e}")

        # Fire first batch
        load_audit_batch()

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    app = BankEnterpriseApp()
    app.mainloop()
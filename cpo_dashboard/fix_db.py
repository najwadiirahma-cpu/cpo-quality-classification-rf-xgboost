import pandas as pd
import joblib
import os
from supabase import create_client

def main():
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    url = secrets["supabase"]["url"]
    key = secrets["supabase"]["key"]
    sb = create_client(url, key)

    # 1. Fetch data
    res = sb.table("riwayat").select("*").execute()
    data = res.data
    
    if not data:
        print("No data found.")
        return

    # Check if we need to predict
    needs_update = []
    
    # Load model just in case
    xgb = joblib.load("models/model_xgb.pkl")
    fitur = ['moisture', 'dirt', 'ffa', 'pv', 'dobi', 'carotene', 'iv']

    for row in data:
        if row.get("hasil_prediksi") is None:
            # If hasil_xgb is somehow still there
            if row.get("hasil_xgb") is not None:
                new_hasil = row["hasil_xgb"]
            else:
                # Re-predict!
                try:
                    df_row = pd.DataFrame([row])[fitur]
                    df_row = df_row.apply(pd.to_numeric, errors='coerce').fillna(df_row.median() if not df_row.empty else 0)
                    pred = int(xgb.predict(df_row)[0])
                    new_hasil = "Baik" if pred == 1 else "Kurang Baik"
                except Exception as e:
                    print(f"Error predicting for row {row['id']}: {e}")
                    continue
            
            needs_update.append((row["id"], new_hasil))

    print(f"Found {len(needs_update)} rows to update.")
    
    # Update rows
    for rid, hasil in needs_update:
        sb.table("riwayat").update({"hasil_prediksi": hasil}).eq("id", rid).execute()
        
    print("Database fix completed successfully.")

if __name__ == "__main__":
    main()

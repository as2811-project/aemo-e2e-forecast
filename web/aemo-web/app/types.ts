export interface PriceData {
    RRP: number
    SETTLEMENTDATE: string
    PeriodType: "Actual" | "Forecast"
  }
  
  export interface ApiResponse {
    statusCode: number
    body: string
  }
    
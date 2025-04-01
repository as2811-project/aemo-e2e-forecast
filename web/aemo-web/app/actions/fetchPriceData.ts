'use server';
const API_URL = process.env.API_URL;
export async function fetchChartData() {
    if (!API_URL) {
        throw new Error("API_URL is not defined");
      }
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ queryType: 'forecast' }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    const rawData = await response.json();
    const parsedBody = JSON.parse(rawData.body);
    return parsedBody;
  } catch (error) {
    console.error(error);
    return null;
  }
}
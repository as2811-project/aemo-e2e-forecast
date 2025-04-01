'use server';

const API_URL = process.env.METADATA_API_URL;

export async function fetchModelMetadata() {
    if (!API_URL) {
        throw new Error("API_URL is not defined");
      }
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ queryType: 'metadata' }),
    });
    console.log(JSON.stringify({ queryType: 'metadata' }))
    if (!response.ok) {
      throw new Error('Failed to fetch model metadata');
    }
    const data = await response.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error(error);
    return null;
  }
}
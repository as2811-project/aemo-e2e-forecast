'use server';
const API_URL = process.env.API_URL;
export async function getPriceSpike() {
    if (!API_URL) {
        throw new Error("API_URL is not defined");
    }
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ queryType: 'spike' }),
        });

        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        const res = await response.json();
        console.log(res);
        
        const messageText = JSON.parse(res.body);
        console.log(messageText);
        return messageText;
    } catch (error) {
        console.error(error);
        return null;
    }
}
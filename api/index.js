export default function handler(req, res) {
  if (req.method === 'GET') {
    res.status(200).json({
      service: 'RIPT Med to Rec Report API',
      status: 'active',
      message: 'Your cannabis reporting API is working!',
      timestamp: new Date().toISOString(),
      endpoints: {
        'GET /api/': 'API status',
        'POST /api/': 'Upload CSV for reports (coming soon)'
      }
    });
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}

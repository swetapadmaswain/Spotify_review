import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

export default async function handler(req: Request, res: Response) {
  if (req.method !== 'GET') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    // Check database connection
    const { error } = await supabase.from('raw_reviews').select('count', { count: 'exact', head: true });
    
    const status = error ? 'unhealthy' : 'healthy';
    
    return new Response(JSON.stringify({
      status,
      timestamp: new Date().toISOString(),
      database: error ? 'disconnected' : 'connected'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      status: 'unhealthy',
      error: 'Health check failed'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

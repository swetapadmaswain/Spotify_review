import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

export default async function handler(req: Request, res: Response) {
  if (req.method !== 'GET') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    const { data: runs, error } = await supabase
      .from('data_collection_runs')
      .select('*')
      .order('start_time', { ascending: false })
      .limit(10);
    
    if (error) throw error;
    
    return new Response(JSON.stringify({ runs }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      error: 'Failed to fetch collection status'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

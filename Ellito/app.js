(function(){
  const logEl = document.getElementById('log')
  function log(v){ logEl.textContent = typeof v === 'string' ? v : JSON.stringify(v,null,2) }

  if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY){
    log('Missing Supabase keys. Copy config.example.js → config.js and fill SUPABASE_URL + SUPABASE_ANON_KEY')
    return
  }

  const supabase = supabaseJs.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY)

  const form = document.getElementById('uploadForm')
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const fileInput = document.getElementById('fileInput')
    const bucket = document.getElementById('bucket').value || 'uploads'
    const folder = document.getElementById('folder').value || ''
    const userFilename = document.getElementById('fileName').value
    const description = document.getElementById('description').value || null

    const file = fileInput.files[0]
    if (!file) return log('Select a file first')

    const fileName = userFilename || file.name
    const timestamp = Date.now()
    const path = (folder ? folder.replace(/(^\/|\/$)/g, '') + '/' : '') + `${timestamp}_${fileName}`

    log('Uploading to bucket "' + bucket + '" as: ' + path)
    const uploadResult = await supabase.storage.from(bucket).upload(path, file, {upsert: false})
    if (uploadResult.error){
      log('Upload error: ' + JSON.stringify(uploadResult.error))
      return
    }

    // get public URL (if bucket has public access) — otherwise you'll need to generate signed URL
    const { data: publicData } = supabase.storage.from(bucket).getPublicUrl(path)
    const publicUrl = publicData?.publicUrl || null

    // store metadata in a table called 'files' (create this table in Supabase)
    const metadata = {
      name: fileName,
      path,
      bucket,
      size: file.size,
      content_type: file.type,
      description,
      url: publicUrl
    }

    const { data: insertData, error: insertError } = await supabase.from('files').insert([metadata])
    if (insertError){
      log('Metadata insert error: ' + JSON.stringify(insertError))
      return
    }

    log('Success!\nUpload: ' + JSON.stringify(uploadResult.data) + '\nMetadata: ' + JSON.stringify(insertData))
  })
})()

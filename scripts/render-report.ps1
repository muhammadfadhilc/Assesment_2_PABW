param(
 [string]$PdfPath = (Join-Path $PSScriptRoot '../output/pdf/707012500122_Muhammad_Fadhil_AsesmenPraktikum2.1_PaketB.pdf')
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
[Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime] | Out-Null
[Windows.Data.Pdf.PdfPageRenderOptions,Windows.Data.Pdf,ContentType=WindowsRuntime] | Out-Null
function Await-Result($Operation, $ResultType) {
 $method=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and $_.GetGenericArguments().Count -eq 1
 } | Select-Object -First 1
 $task=$method.MakeGenericMethod($ResultType).Invoke($null,@($Operation))
 $task.Wait()
 return $task.Result
}
function Await-Action($Action) {
 $method=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and -not $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction'
 } | Select-Object -First 1
 $task=$method.Invoke($null,@($Action))
 $task.Wait()
}
$inputFile=Await-Result ([Windows.Storage.StorageFile]::GetFileFromPathAsync([System.IO.Path]::GetFullPath($PdfPath))) ([Windows.Storage.StorageFile])
$pdf=Await-Result ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($inputFile)) ([Windows.Data.Pdf.PdfDocument])
$dir=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../tmp/pdfs'))
[System.IO.Directory]::CreateDirectory($dir) | Out-Null
for ($i=0; $i -lt $pdf.PageCount; $i++) {
 $page=$pdf.GetPage($i)
 $stream=New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
 $options=New-Object Windows.Data.Pdf.PdfPageRenderOptions
 $options.DestinationWidth=1000
 Await-Action ($page.RenderToStreamAsync($stream,$options))
 $read=[System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
 $file=[System.IO.File]::Create((Join-Path $dir ('page-{0:D2}.png' -f ($i+1))))
 $read.CopyTo($file)
 $file.Dispose();$read.Dispose();$stream.Dispose();$page.Dispose()
}
Add-Type -AssemblyName System.Drawing
$sheet=New-Object System.Drawing.Bitmap(1000,1516)
$g=[System.Drawing.Graphics]::FromImage($sheet)
$g.Clear([System.Drawing.Color]::FromArgb(222,228,224))
for ($i=0; $i -lt $pdf.PageCount; $i++) {
 $im=[System.Drawing.Image]::FromFile((Join-Path $dir ('page-{0:D2}.png' -f ($i+1))))
 $x=($i%4)*250+8;$y=[Math]::Floor($i/4)*379+8
 $g.DrawImage($im,[int]$x,[int]$y,234,331)
 $im.Dispose()
}
$g.Dispose();$sheet.Save((Join-Path $dir 'contact-sheet.png'));$sheet.Dispose()
Write-Output ('Rendered {0} PDF pages to {1}' -f $pdf.PageCount,$dir)

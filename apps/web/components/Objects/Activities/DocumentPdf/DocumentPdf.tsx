import { useOrg } from '@components/Contexts/OrgContext'
import { getActivityMediaDirectory } from '@services/media/media'
import React from 'react'

function DocumentPdfActivity({
  activity,
  course,
}: {
  activity: any
  course: any
}) {
  const org = useOrg() as any

  React.useEffect(() => {
  }, [activity, org])

  // Use S3 file_url directly
  const pdfSrc = activity.content?.file_url

  return (
    <div className="m-8 bg-zinc-900 rounded-md mt-14">
      {pdfSrc ? (
        <iframe
          className="rounded-lg w-full h-[900px]"
          src={pdfSrc}
        />
      ) : (
        <div className="flex items-center justify-center h-[900px] text-gray-500">
          <div className="text-center">
            <p className="text-lg font-medium">PDF không khả dụng</p>
            <p className="text-sm mt-2">Vui lòng tải lại file này</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default DocumentPdfActivity

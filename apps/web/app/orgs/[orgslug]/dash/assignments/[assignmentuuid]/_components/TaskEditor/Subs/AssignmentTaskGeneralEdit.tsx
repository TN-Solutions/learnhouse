'use client'
import { useAssignments } from '@components/Contexts/Assignments/AssignmentContext'
import {
  useAssignmentsTask,
  useAssignmentsTaskDispatch,
} from '@components/Contexts/Assignments/AssignmentsTaskContext'
import { useLHSession } from '@components/Contexts/LHSessionContext'
import { useOrg } from '@components/Contexts/OrgContext'
import FormLayout, {
  FormField,
  FormLabelAndMessage,
  Input,
  Textarea,
} from '@components/Objects/StyledElements/Form/Form'
import * as Form from '@radix-ui/react-form'
import { getActivityByID } from '@services/courses/activities'
import { updateAssignmentTask } from '@services/courses/assignments'
import {
  getTaskRefFileDir,
  getMediaUrlFromFileUrl,
} from '@services/media/media'
import { getAPIUrl } from '@services/config/config'
import { useFileUpload } from '@/hooks/useFileUpload'
import { useFormik } from 'formik'
import { Cloud, File, Info, Loader, UploadCloud } from 'lucide-react'
import Link from 'next/link'
import React, { useEffect } from 'react'
import toast from 'react-hot-toast'
import { constructAcceptValue } from '@/lib/constants'

const SUPPORTED_FILES = constructAcceptValue([
  'pdf',
  'docx',
  'mp4',
  'jpg',
  'png',
  'pptx',
  'zip',
])

export function AssignmentTaskGeneralEdit() {
  const session = useLHSession() as any
  const access_token = session?.data?.tokens?.access_token
  const assignmentTaskState = useAssignmentsTask() as any
  const assignmentTaskStateHook = useAssignmentsTaskDispatch() as any
  const assignment = useAssignments() as any

  const validate = (values: any) => {
    const errors: any = {}
    if (values.max_grade_value < 20 || values.max_grade_value > 100) {
      errors.max_grade_value = 'Value should be between 20 and 100'
    }
    return errors
  }

  const formik = useFormik({
    initialValues: {
      title: assignmentTaskState.assignmentTask.title,
      description: assignmentTaskState.assignmentTask.description,
      hint: assignmentTaskState.assignmentTask.hint,
      max_grade_value: assignmentTaskState.assignmentTask.max_grade_value,
    },
    validate,
    onSubmit: async (values) => {
      const res = await updateAssignmentTask(
        values,
        assignmentTaskState.assignmentTask.assignment_task_uuid,
        assignment.assignment_object.assignment_uuid,
        access_token
      )
      if (res) {
        assignmentTaskStateHook({ type: 'reload' })
        toast.success('Task updated successfully')
      } else {
        toast.error('Error updating task, please retry later.')
      }
    },
    enableReinitialize: true,
  }) as any

  return (
    <FormLayout onSubmit={formik.handleSubmit}>
      <FormField name="title">
        <FormLabelAndMessage label="Title" message={formik.errors.title} />
        <Form.Control asChild>
          <Input
            onChange={formik.handleChange}
            value={formik.values.title}
            type="text"
          />
        </Form.Control>
      </FormField>

      <FormField name="description">
        <FormLabelAndMessage
          label="Description"
          message={formik.errors.description}
        />
        <Form.Control asChild>
          <Input
            onChange={formik.handleChange}
            value={formik.values.description}
            type="text"
          />
        </Form.Control>
      </FormField>

      <FormField name="hint">
        <FormLabelAndMessage label="Hint" message={formik.errors.hint} />
        <Form.Control asChild>
          <Textarea onChange={formik.handleChange} value={formik.values.hint} />
        </Form.Control>
      </FormField>

      <FormField name="hint">
        <div className="flex space-x-3 justify-between items-center">
          <FormLabelAndMessage
            label="Reference file"
            message={formik.errors.hint}
          />
          <div className="flex space-x-1.5 text-xs items-center text-gray-500 ">
            <Info size={16} />
            <p>Allowed formats : pdf, docx, mp4, jpg, jpeg, png, pptx, zip</p>
          </div>
        </div>
        <Form.Control asChild>
          <UpdateTaskRef />
        </Form.Control>
      </FormField>

      <FormField name="max_grade_value">
        <FormLabelAndMessage
          label="Max Grade Value"
          message={formik.errors.max_grade_value}
        />
        <Form.Control asChild>
          <Input
            onChange={formik.handleChange}
            value={formik.values.max_grade_value}
            type="number"
          />
        </Form.Control>
      </FormField>

      {/* Submit button */}
      <Form.Submit>
        <button
          type="submit"
          className="flex items-center justify-center w-full px-4 py-2 mt-4 font-semibold text-white bg-green-500 rounded-md hover:bg-green-600"
        >
          Submit
        </button>
      </Form.Submit>
    </FormLayout>
  )
}

function UpdateTaskRef() {
  const session = useLHSession() as any
  const org = useOrg() as any
  const access_token = session?.data?.tokens?.access_token
  const assignmentTaskState = useAssignmentsTask() as any
  const assignmentTaskStateHook = useAssignmentsTaskDispatch() as any
  const assignment = useAssignments() as any
  const [error, setError] = React.useState('') as any
  const [activity, setActivity] = React.useState('') as any

  // Use the new upload hook
  const { upload, isLoading, progress } = useFileUpload()

  const handleFileChange = async (event: any) => {
    const file = event.target.files[0]
    if (!file) return

    // Upload file using the new hook
    const result = await upload({
      file: file,
      resourceType: 'assignment_reference',
      resourceId: assignmentTaskState.assignmentTask.assignment_task_uuid,
      fileCategory: 'document', // Default category, can be enhanced based on file type
    })

    if (result.success) {
      // Update assignment task with the new file URL
      try {
        const response = await fetch(
          `${getAPIUrl()}assignments/${assignment.assignment_object.assignment_uuid}/tasks/${assignmentTaskState.assignmentTask.assignment_task_uuid}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${access_token}`,
            },
            body: JSON.stringify({
              reference_file: result.fileUrl,
            }),
          }
        )

        if (response.ok) {
          assignmentTaskStateHook({ type: 'reload' })
          toast.success('Reference file updated successfully')
          setError('')
        } else {
          const errorData = await response.json()
          setError(errorData.detail || 'Failed to update reference file')
        }
      } catch (err) {
        setError('Failed to update reference file')
      }
    } else {
      setError(result.error || 'Failed to upload file')
    }

    // wait for 1 second to show loading animation
    await new Promise((r) => setTimeout(r, 1500))
  }

  const getTaskRefDirUI = () => {
    return getTaskRefFileDir(
      org?.org_uuid,
      assignment.course_object.course_uuid,
      assignment.activity_object.activity_uuid,
      assignment.assignment_object.assignment_uuid,
      assignmentTaskState.assignmentTask.assignment_task_uuid,
      assignmentTaskState.assignmentTask.reference_file
    )
  }

  const deleteReferenceFile = async () => {
    try {
      const response = await fetch(
        `${getAPIUrl()}assignments/${assignment.assignment_object.assignment_uuid}/tasks/${assignmentTaskState.assignmentTask.assignment_task_uuid}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${access_token}`,
          },
          body: JSON.stringify({
            reference_file: '',
          }),
        }
      )

      if (response.ok) {
        assignmentTaskStateHook({ type: 'reload' })
        setError('')
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to delete reference file')
      }
    } catch (err) {
      setError('Failed to delete reference file')
    }

    // wait for 1 second to show loading animation
    await new Promise((r) => setTimeout(r, 1500))
  }

  async function getActivityUI() {
    const res = await getActivityByID(
      assignment.assignment_object.activity_id,
      null,
      access_token
    )
    setActivity(res.data)
  }

  useEffect(() => {
    getActivityUI()
  }, [assignmentTaskState, org])

  return (
    <div className="w-auto bg-gray-50 rounded-xl outline outline-1 outline-gray-200 h-[200px] shadow-sm">
      <div className="flex flex-col justify-center items-center h-full">
        <div className="flex flex-col justify-center items-center">
          <div className="flex flex-col justify-center items-center">
            {error && (
              <div className="flex justify-center bg-red-200 rounded-md text-red-950 space-x-2 items-center p-2 transition-all shadow-xs">
                <div className="text-sm font-semibold">{error}</div>
              </div>
            )}
          </div>
          {assignmentTaskState.assignmentTask.reference_file && !isLoading && (
            <div className="flex flex-col rounded-lg bg-white text-gray-400 shadow-lg nice-shadow px-5 py-3 space-y-1 items-center relative">
              <div className="absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2 bg-green-500 rounded-full px-1.5 py-1.5 text-white flex justify-center items-center">
                <Cloud size={15} />
              </div>
              <File size={20} className="" />
              <div className="font-semibold text-sm uppercase">
                {assignmentTaskState.assignmentTask.reference_file
                  .split('.')
                  .pop()}
              </div>
              <div className="flex space-x-2 mt-2">
                <Link
                  href={getMediaUrlFromFileUrl(getTaskRefDirUI())}
                  download
                  target="_blank"
                  className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-semibold"
                >
                  Download
                </Link>
                {/** <button onClick={() => deleteReferenceFile()}
                                    className='bg-red-500 text-white px-3 py-1 rounded-full text-xs font-semibold'>Delete</button> */}
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="flex justify-center items-center">
              <input
                type="file"
                accept={SUPPORTED_FILES}
                id="fileInput"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              <div className="font-bold animate-pulse antialiased items-center bg-slate-200 text-gray text-sm rounded-md px-4 py-2 mt-4 flex flex-col">
                <Loader size={16} className="mr-2" />
                <span>Uploading... {progress}%</span>
              </div>
            </div>
          ) : (
            <div className="flex justify-center items-center">
              <input
                type="file"
                accept={SUPPORTED_FILES}
                id="fileInput"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              <button
                className="font-bold antialiased items-center text-gray text-sm rounded-md px-4 mt-6 flex"
                onClick={() => document.getElementById('fileInput')?.click()}
              >
                <UploadCloud size={16} className="mr-2" />
                <span>Change Reference File</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

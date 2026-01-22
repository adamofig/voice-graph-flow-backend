/**
 * Example Next.js Server Action or API Route function to send a file to the FastAPI Docling service.
 */
export async function convertFileToMarkdown(file: File) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8000/convert', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to convert document');
        }

        const data = await response.json();
        return data.markdown; // returns the markdown string
    } catch (error) {
        console.error('Error in convertFileToMarkdown:', error);
        throw error;
    }
}
